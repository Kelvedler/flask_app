import json
import re
from flask import Response
from marshmallow import ValidationError

from common import constants as con, regex

SCHEMA_ERROR = '_schema'


class BaseResponse(Response):
    status_code = 500
    _reason_phrase = 'internal'

    def __init__(self, *errors, **kwargs):
        self._errors = errors
        super().__init__(self.response_dict, status=self.status_code, mimetype='application/json', **kwargs)

    @property
    def response_dict(self):
        return json.dumps({'errors': self._errors if self._errors else [self._reason_phrase]})

    def as_error_handler(self, err):
        return self.response_dict, self.status_code


class BadRequest(BaseResponse):
    status_code = 400
    _reason_phrase = 'bad_request'


class Unauthorized(BaseResponse):
    status_code = 401
    _reason_phrase = 'request__unauthorized'


class Forbidden(BaseResponse):
    status_code = 403
    _reason_phrase = 'request__forbidden'


class NotFound(BaseResponse):
    status_code = 404
    _reason_phrase = 'not_found'


class ServerInternalError(BaseResponse):
    pass


class ServerUnavailable(BaseResponse):
    status_code = 503
    _reason_phrase = 'unavailable'


def get_response_code(*codes):
    code_priority = 400, 403, 404
    response_code = codes[0]
    for code in codes:
        if code_priority.index(code) < code_priority.index(response_code):
            response_code = code
    return response_code


error_dict = {
    con.ERROR_REQUIRED: (
        'Missing data for required field.',
        'Field may not be null.'
    )
}


def normalize_message(message):
    for normalized, denormalized_list in error_dict.items():
        if message in denormalized_list:
            return normalized
    return con.ERROR_INVALID


def determine_code_from_message(message):
    error_codes = {
        con.ERROR_INVALID: 400,
        con.ERROR_REQUIRED: 400,
        con.ERROR_FORBIDDEN: 403,
        con.NOT_FOUND: 404
    }
    return error_codes.get(message, 400)


def prioritize_message(message_dict, code):
    messages = []
    prioritized_message_found = False
    for message, message_code in message_dict.items():
        if code == message_code and not prioritized_message_found:
            messages.insert(0, message)
            prioritized_message_found = True
        else:
            messages.append(message)
    return messages


def convert_from_validation(validation_err: ValidationError):
    normalized_dict = {}
    pattern = re.compile(regex.ERROR_RESPONSE)
    for field, errs in validation_err.messages_dict.items():
        for err in errs:
            message = err if pattern.search(err) else normalize_message(err)
            err_message = f'{field}__{message}' if field != SCHEMA_ERROR else message
            normalized_dict[err_message] = determine_code_from_message(message)
    response_code = get_response_code(*list(normalized_dict.values()))
    errors = prioritize_message(normalized_dict, response_code)
    responses = [BadRequest, Forbidden, NotFound]
    for response in responses:
        if response.status_code == response_code:
            return response(*errors)
    return BadRequest(*errors)
