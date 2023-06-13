import json
import logging
from flask import Blueprint

from app_core.api import JsonResponse, error_response as err_resp
from app_core.elastic import client as elastic_client
from .common import get_src

logger = logging.getLogger(__name__)

titles = Blueprint('titles', __name__, url_prefix='titles/')


@titles.route('', methods=['GET'])
def titles_view():
    src, err = get_src(required=True)
    if err:
        return err
    results = []
    try:
        suggests = elastic_client.search(index='posts', suggest={'title_suggestions': {
            'text': src,
            'completion': {
                'field': 'title_suggest',
                'skip_duplicates': True,
                'fuzzy': {
                    'fuzziness': 'auto'
                }
            }
        }})['suggest']['title_suggestions'][0]['options']
    except Exception as e:
        logger.exception(e)
        return err_resp.ServerInternalError()
    for suggest in suggests:
        results.append({'id': suggest['_id'], 'title': suggest['_source']['title']})
    return JsonResponse(json.dumps(results), status=200)
