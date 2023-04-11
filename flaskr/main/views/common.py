import json

from common import conv, constants
from common.api import JsonResponse
from config import config
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
        expires=conv.to_ts(conv.get_now() + config.JWT_REFRESH_EXPIRATION_TIMEDELTA)
    )
    return response
