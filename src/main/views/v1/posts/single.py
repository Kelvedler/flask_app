from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import select, exc, update, delete

from app_core.api import convert_from_validation, JsonResponse, error_response as err_resp
from app_core.db import engine
from app_core.jwt_ import jwt_access_required
from main.models.post import post_table, PostSchema, PostSchemaFromFlat, post_update_queue
from .common import get_post
from .comments import comments

single = Blueprint('single', __name__, url_prefix='/<post_id>')
single.register_blueprint(comments)


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


@single.route('', methods=['GET', 'PUT', 'DELETE'])
@jwt_access_required(exclude_methods=['GET'])
def single_view(post_id):
    if request.method == 'GET':
        post, err = get_post(post_id)
        if err:
            return err
        return JsonResponse(PostSchemaFromFlat().dumps(post._asdict()), status=200)

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
