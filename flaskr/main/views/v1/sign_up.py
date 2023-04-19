from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import insert
from sqlalchemy.sql.expression import literal_column

from app_core.api import convert_from_validation
from app_core.db import engine
from main.models.person import person_table, InsertPersonSchema, hash_password
from main.views.common import person_tokens_response

sign_up = Blueprint('sign-up', __name__, url_prefix='sign-up')


@sign_up.route('', methods=('POST',))
def sign_up_view():
    try:
        data = InsertPersonSchema().load(request.json)
    except ValidationError as err:
        return convert_from_validation(err)
    data['password'] = hash_password(data['password'])
    with engine.connect() as conn:
        person = conn.execute(insert(person_table).values(**data).returning(literal_column('id'))).one()._asdict()
        conn.commit()
    return person_tokens_response(str(person['id']), status=201)
