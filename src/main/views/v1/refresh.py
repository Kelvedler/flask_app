from flask import Blueprint, request

from app_core.jwt_ import jwt_refresh_required
from main.views.common import person_access_token_response

refresh = Blueprint('refresh', __name__, url_prefix='refresh')


@refresh.route('', methods=['POST'])
@jwt_refresh_required()
def refresh_view():
    return person_access_token_response(str(request.person['id']), 200)
