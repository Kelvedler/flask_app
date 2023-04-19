from argon2 import PasswordHasher, exceptions
from marshmallow import ValidationError, fields, validate, validates
from sqlalchemy import Table, Column, String, select, TIMESTAMP
from sqlalchemy.sql import func

from app_core.constants import PERSON_ACCESS, PERSON_REFRESH
from app_core.regex import PASSWORD as RE_PASSWORD
from app_core.db import engine
from main.models.base import metadata_obj, get_base_columns, BaseSchema

person_table = Table(
    'person',
    metadata_obj,
    *get_base_columns(),
    Column('name', String(50), nullable=False, unique=True),
    Column('email', String(50), nullable=False, unique=True),
    Column('password', String(256), nullable=False),
    Column('password_updated_at', TIMESTAMP(timezone=True), default=func.timezone('UTC', func.current_timestamp()), nullable=False),
)


class PersonSchema(BaseSchema):
    name = fields.String(validate=validate.Length(min=3, max=50), required=True)
    email = fields.Email(validate=validate.Length(max=50), required=True)
    password = fields.String(validate=validate.Regexp(RE_PASSWORD), required=True, load_only=True)


class InsertPersonSchema(PersonSchema):
    @validates('name')
    def validate_name(self, value):
        with engine.connect() as conn:
            result = conn.execute(select(person_table.c.id).where(person_table.c.name == value))
            if result.rowcount > 0:
                raise ValidationError('exists')

    @validates('email')
    def validate_email(self, value):
        with engine.connect() as conn:
            result = conn.execute(select(person_table.c.id).where(person_table.c.email == value))
            if result.rowcount > 0:
                raise ValidationError('exists')


def hash_password(raw_password):
    return PasswordHasher().hash(raw_password)


def is_password_valid(raw_password, hashed_password):
    try:
        PasswordHasher().verify(hashed_password, raw_password)
        return True
    except exceptions.Argon2Error:
        return False


def encode_access_token(person_id):
    from app_core.jwt_ import encode
    return encode(person_id, PERSON_ACCESS)


def encode_refresh_token(person_id):
    from app_core.jwt_ import encode
    return encode(person_id, PERSON_REFRESH)
