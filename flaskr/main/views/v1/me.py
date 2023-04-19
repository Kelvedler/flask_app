from flask import Blueprint, request
from marshmallow import Schema, fields, validate, validates, post_load, ValidationError
from sqlalchemy import update

from app_core import time
from app_core.api import convert_from_validation, JsonResponse
from app_core.jwt_ import jwt_access_required
from app_core.regex import PASSWORD as RE_PASSWORD
from app_core.db import engine
from main.models.person import PersonSchema, is_password_valid, person_table, hash_password

me = Blueprint('me', __name__, url_prefix='me')

password = Blueprint('password', __name__, url_prefix='/password')
me.register_blueprint(password)


class PasswordSchema(Schema):
    old_password = fields.String(validate=validate.Regexp(RE_PASSWORD), required=True)
    new_password = fields.String(validate=validate.Regexp(RE_PASSWORD), required=True)

    @validates('old_password')
    def validate_old_password(self, value):
        if not is_password_valid(value, self.context['person']['password']):
            raise ValidationError('invalid', field_name='old_password')
        return value

    @post_load
    def are_passwords_same(self, data, **kwargs):
        if data['old_password'] == data['new_password']:
            raise ValidationError('password__same')
        return data


@me.route('', methods=['GET'])
@jwt_access_required()
def me_view():
    return JsonResponse(PersonSchema().dumps(request.person), status=200)


@password.route('', methods=['POST'])
@jwt_access_required()
def password_view():
    person = request.person
    try:
        schema = PasswordSchema()
        schema.context['person'] = person
        data = schema.load(request.json)
    except ValidationError as err:
        return convert_from_validation(err)
    hashed_password = hash_password(data['new_password'])
    with engine.connect() as conn:
        conn.execute(update(person_table).where(person_table.c.id == person['id']).values(
            password=hashed_password, password_updated_at=time.get_now()))
        conn.commit()
    return JsonResponse(PersonSchema().dumps(person), status=200)
