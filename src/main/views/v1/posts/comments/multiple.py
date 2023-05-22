from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import insert, select

from app_core.api import JsonResponse, convert_from_validation
from app_core.db import engine, label_columns
from app_core.jwt_ import jwt_access_required
from app_core.rabbitmq import broadcast_comment
from main.models.post import post_comment_table, PostCommentSchema, PostCommentSchemaFromFlat
from main.models.person import person_table
from ..common import get_post

multiple = Blueprint('', __name__, url_prefix='')

POST_COMMENT_SUBSCRIPTION = '/v1/posts/{}/comments/'


def get_post_comments(post):
    with engine.connect() as conn:
        post_comments = conn.execute(select(
            *label_columns(post_comment_table), *label_columns(person_table)
        ).where(
            post_comment_table.c.post == post.get('post__id'),
            post_comment_table.c.person == person_table.c.id
        )).all()
    return JsonResponse(PostCommentSchemaFromFlat(many=True).dumps(
        [post_comment._asdict() for post_comment in post_comments]
    ), status=200)


def create_post_comment(post):
    post_id = post.get('post__id')
    post_comment_schema = PostCommentSchema()
    person = request.person
    try:
        data = post_comment_schema.load(request.json)
    except ValidationError as err:
        return convert_from_validation(err)
    data['person'] = person.get('id')
    data['post'] = post_id
    with engine.connect() as conn:
        post_comment = conn.execute(
            insert(post_comment_table).values(**data).returning(post_comment_table)
        ).one()._asdict()
        conn.commit()
    post_comment['person'] = person
    post_comment_repr = post_comment_schema.dumps(post_comment)
    broadcast_comment(post_comment_repr, POST_COMMENT_SUBSCRIPTION.format(post_id))
    return JsonResponse(post_comment_repr, status=201)


@multiple.route('', methods=['GET', 'POST'])
@jwt_access_required(exclude_methods=['GET'])
def multiple_view(post_id):
    post, err = get_post(post_id)
    if err:
        return err
    if request.method == 'GET':
        return get_post_comments(post._asdict())
    elif request.method == 'POST':
        return create_post_comment(post._asdict())
