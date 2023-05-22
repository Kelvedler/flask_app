import json
import logging
from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import insert, select

from app_core.api import convert_from_validation, JsonResponse, error_response as err_resp
from app_core.db import engine, label_columns
from app_core.elastic import client as elastic_client
from app_core.jwt_ import jwt_access_required
from main.models.post import post_table, PostSchema, PostSchemaFromFlat, post_update_queue
from main.models.person import person_table
from .common import get_src

logger = logging.getLogger(__name__)

multiple = Blueprint('', __name__, url_prefix='')


def get_posts():
    src, err = get_src()
    if err:
        return err

    query = []
    if src:
        try:
            hits = elastic_client.search(index='posts', filter_path=['hits.hits._id'],
                                         query={'query_string': {'query': f'text:{src}~'}}
                                         )['hits']['hits']
        except KeyError:
            return JsonResponse(json.dumps({}), status=200)
        except Exception as e:
            logger.exception(e)
            return err_resp.ServerInternalError()
        else:
            query.append(post_table.c.id.in_([hit['_id'] for hit in hits]))
    with engine.connect() as conn:
        posts = conn.execute(select(
            *label_columns(post_table), *label_columns(person_table)
        ).where(post_table.c.person == person_table.c.id, *query)).all()
    return JsonResponse(PostSchemaFromFlat(many=True).dumps([post._asdict() for post in posts]), status=200)


def create_post():
    post_schema = PostSchema()
    person = request.person
    try:
        data = post_schema.load(request.json)
    except ValidationError as err:
        return convert_from_validation(err)
    data['person'] = person.get('id')
    with engine.connect() as conn:
        post = conn.execute(insert(post_table).values(**data).returning(post_table)).one()._asdict()
        conn.commit()
        post_update_queue.add_objects(post['id'])
    post['person'] = person
    return JsonResponse(post_schema.dumps(post), status=201)


@multiple.route('', methods=['GET', 'POST'])
@jwt_access_required(exclude_methods=['GET'])
def multiple_view():
    if request.method == 'GET':
        return get_posts()
    elif request.method == 'POST':
        return create_post()
