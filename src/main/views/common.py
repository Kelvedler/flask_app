import json

from app_core import time, constants
from app_core.api import JsonResponse
from app_core.config import config
from main.models.person import encode_access_token, encode_refresh_token


def person_access_token_response(person_id: str, status: int):
    return JsonResponse(json.dumps({
        'access_token': encode_access_token(person_id)
    }), status=status)


def person_tokens_response(person_id: str, status: int):
    response = person_access_token_response(person_id, status)
    response.set_cookie(
        key=constants.REFRESH_COOKIE_NAME,
        value=encode_refresh_token(person_id),
        expires=time.to_ts(time.get_now() + config.JWT_REFRESH_EXPIRATION_TIMEDELTA)
    )
    return response
