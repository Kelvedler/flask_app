import json
import logging
from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import insert, select, exc, update, delete

from app_core.api import convert_from_validation, JsonResponse, error_response as err_resp
from app_core.db import engine, label_columns
from app_core.elastic import client as elastic_client
from app_core.jwt_ import jwt_access_required
from app_core.schemas import get_src_schema
from main.models.post import post_table, PostSchema, PostSchemaFromFlat, post_update_queue
from main.models.person import person_table

logger = logging.getLogger(__name__)


posts = Blueprint('posts', __name__, url_prefix='posts/')
titles = Blueprint('titles', __name__, url_prefix='titles/')
single = Blueprint('single', __name__, url_prefix='/<post_id>')
posts.register_blueprint(titles)
posts.register_blueprint(single)


def get_src(required=False):
    try:
        data = get_src_schema(required)().load(request.args)
    except ValidationError as err:
        return None, convert_from_validation(err)
    return data.get('src'), None


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


def get_post(post_id):
    try:
        with engine.connect() as conn:
            post = conn.execute(select(
                *label_columns(post_table), *label_columns(person_table)
            ).where(post_table.c.id == post_id, post_table.c.person == person_table.c.id)).one()
    except (exc.NoResultFound, exc.DataError):
        return err_resp.NotFound('post__not_found')
    return JsonResponse(PostSchemaFromFlat().dumps(post._asdict()), status=200)


def put_post(post_id):
    post_schema = PostSchema()
    try:
        data = post_schema.load(request.json)
    except ValidationError as err:
        return convert_from_validation(err)
    with engine.connect() as conn:
        post = conn.execute(update(post_table).where(post_table.c.id == post_id)
                            .values(text=data.get('text'), title=data.get('title'))
                            .returning(post_table)).one()._asdict()
        conn.commit()
        post_update_queue.add_objects(post_id)
    post['person'] = request.person
    return JsonResponse(post_schema.dumps(post), status=200)


def delete_post(post_id):
    with engine.connect() as conn:
        conn.execute(delete(post_table).where(post_table.c.id == post_id))
        conn.commit()
        post_update_queue.add_objects(post_id)
    return JsonResponse({}, status=204)


@posts.route('', methods=['GET', 'POST'])
@jwt_access_required(exclude_methods=['GET'])
def multiple_view():
    if request.method == 'GET':
        return get_posts()
    elif request.method == 'POST':
        return create_post()


@titles.route('', methods=['GET'])
def titles_view():
    src, err = get_src(required=True)
    if err:
        return err
    results = []
    try:
        suggests = elastic_client.search(index='posts', suggest={'title_suggestions': {
            'text': src,
            'completion': {
                'field': 'title_suggest',
                'skip_duplicates': True,
                'fuzzy': {
                    'fuzziness': 'auto'
                }
            }
        }})['suggest']['title_suggestions'][0]['options']
    except Exception as e:
        logger.exception(e)
        return err_resp.ServerInternalError()
    for suggest in suggests:
        results.append({'id': suggest['_id'], 'title': suggest['_source']['title']})
    return JsonResponse(json.dumps(results), status=200)


@single.route('', methods=['GET', 'PUT', 'DELETE'])
@jwt_access_required(exclude_methods=['GET'])
def single_view(post_id):
    if request.method == 'GET':
        return get_post(post_id)

    try:
        with engine.connect() as conn:
            post = conn.execute(select(post_table).where(post_table.c.id == post_id)).one()
    except (exc.NoResultFound, exc.DataError):
        return err_resp.NotFound('post__not_found')
    if post._asdict().get('person') != request.person.get('id'):
        return err_resp.Forbidden('action__not_allowed')

    if request.method == 'PUT':
        return put_post(post_id)
    elif request.method == 'DELETE':
        return delete_post(post_id)
