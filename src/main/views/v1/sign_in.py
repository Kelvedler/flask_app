from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy import select, exc

from app_core.api import convert_from_validation, BadRequest
from app_core.db import engine
from main.models.person import PersonSchema, person_table, is_password_valid
from main.views.common import person_tokens_response

sign_in = Blueprint('sign-in', __name__, url_prefix='sign-in')


@sign_in.route('', methods=['POST'])
def sign_in_view():
    try:
        data = PersonSchema(only=['name', 'password']).load(request.json)
    except ValidationError as err:
        return convert_from_validation(err)
    with engine.connect() as conn:
        try:
            person = conn.execute(
                select(person_table.c.id, person_table.c.password).where(person_table.c.name == data['name'])
            ).one()._asdict()
            assert is_password_valid(data['password'], person['password'])
        except (exc.NoResultFound, AssertionError):
            return BadRequest('bad_credentials')
        else:
            return person_tokens_response(str(person['id']), 200)
