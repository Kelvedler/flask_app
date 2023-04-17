from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import insert, select, exc, update, delete

from common.api import convert_from_validation, JsonResponse, error_response as err_resp
from common.db import label_columns
from common.jwt_ import jwt_access_required
from db import engine
from main.models.post import post_table, PostSchema, PostSchemaFromFlat
from main.models.person import person_table


posts = Blueprint('posts', __name__, url_prefix='posts/')
single = Blueprint('single', __name__, url_prefix='/<post_id>')
posts.register_blueprint(single)


def get_posts():
    with engine.connect() as conn:
        posts = conn.execute(select(
            *label_columns(post_table), *label_columns(person_table)
        ).where(post_table.c.person == person_table.c.id)).all()
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
    post['person'] = request.person
    return JsonResponse(post_schema.dumps(post), status=200)


def delete_post(post_id):
    with engine.connect() as conn:
        conn.execute(delete(post_table).where(post_table.c.id == post_id))
        conn.commit()
    return JsonResponse({}, status=204)


@posts.route('', methods=['GET', 'POST'])
@jwt_access_required(exclude_methods=['GET'])
def multiple_view():
    if request.method == 'GET':
        return get_posts()
    elif request.method == 'POST':
        return create_post()


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
