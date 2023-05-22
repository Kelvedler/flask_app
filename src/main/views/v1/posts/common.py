from flask import request
from marshmallow import ValidationError
from sqlalchemy import select, exc

from app_core.api import convert_from_validation, error_response as err_resp
from app_core.db import engine, label_columns
from app_core.schemas import get_src_schema
from main.models.post import post_table
from main.models.person import person_table


def get_src(required=False):
    try:
        data = get_src_schema(required)().load(request.args)
    except ValidationError as err:
        return None, convert_from_validation(err)
    return data.get('src'), None


def get_post(post_id):
    try:
        with engine.connect() as conn:
            return conn.execute(select(
                *label_columns(post_table), *label_columns(person_table)
            ).where(post_table.c.id == post_id, post_table.c.person == person_table.c.id)).one(), None
    except (exc.NoResultFound, exc.DataError):
        return None, err_resp.NotFound('post__not_found')
