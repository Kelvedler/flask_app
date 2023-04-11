import re
import jwt
from datetime import datetime
from flask import request
from sqlalchemy import select, exc

from common import conv
from common.api import error_response as err_resp
from common.constants import PERSON_ACCESS, PERSON_REFRESH, REFRESH_COOKIE_NAME
from config import config
from db import engine
from main.models.person import person_table

JWT_ALGORITHM = 'HS256'
JWT_PAYLOAD_KEYS = 'id', 'type', 'ts'

EXPIRATION_FOR_TYPE = {
    PERSON_ACCESS: config.JWT_ACCESS_EXPIRATION_TIMEDELTA,
    PERSON_REFRESH: config.JWT_REFRESH_EXPIRATION_TIMEDELTA,
}


def encode(identifier, type_):
    payload = {
        'id': identifier,
        'type': type_,
        'ts': conv.get_now_ts()
    }
    token = jwt.encode(payload, config.SECRET_KEY, JWT_ALGORITHM)
    return token


def decode(encoded):
    try:
        return jwt.decode(encoded, config.SECRET_KEY, JWT_ALGORITHM)
    except (jwt.DecodeError, jwt.InvalidTokenError, jwt.ExpiredSignatureError):
        return False


def jwt_(type_, get_token, required=True):
    def decorator(function):
        def wrapper(*args, **kwargs):
            try:
                decoded = decode(get_token())
                assert decoded
                assert all(key in decoded for key in JWT_PAYLOAD_KEYS)
                assert decoded['ts'] > conv.to_ts(conv.get_now() - EXPIRATION_FOR_TYPE[type_])
                assert decoded['type'] == type_
                with engine.connect() as conn:
                    person = conn.execute(select(person_table).where(
                        person_table.c.id == decoded['id'],
                        person_table.c.password_updated_at < datetime.utcfromtimestamp(decoded['ts'])
                    )).one()
            except (AssertionError, exc.NoResultFound, exc.DataError):
                if required:
                    return err_resp.Unauthorized()
                else:
                    request.person = None
                    return function(*args, **kwargs)
            else:
                request.person = person._asdict()
                return function(*args, **kwargs)
        return wrapper
    return decorator


def jwt_from_headers(type_, required=True):
    def get_from_headers():
        bearer = request.headers.environ.get('HTTP_AUTHORIZATION')
        assert bearer
        bearer_pattern = re.search(r'Bearer (.+)', bearer)
        assert bearer_pattern
        return bearer_pattern.group(1)

    return jwt_(type_, get_from_headers, required)


def jwt_from_cookies(type_, required=True):
    def get_from_cookies():
        token = request.cookies.get(REFRESH_COOKIE_NAME)
        assert token
        return token

    return jwt_(type_, get_from_cookies, required)


jwt_access_required = jwt_from_headers(PERSON_ACCESS)
jwt_refresh_required = jwt_from_cookies(PERSON_REFRESH)
