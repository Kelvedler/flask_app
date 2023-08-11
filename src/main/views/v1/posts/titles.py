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
        suggests = elastic_client.search(index='posts', query={
            'multi_match': {
                'query': src,
                'type': 'bool_prefix',
                'fields': [
                    'title_search_as_type',
                    'title_search_as_type._2gram',
                    'title_search_as_type._3gram'
                ]
            }
        }).body['hits']['hits']
    except Exception as e:
        logger.exception(e)
        return err_resp.ServerInternalError()
    for suggest in suggests:
        results.append({'id': suggest['_id'], 'title': suggest['_source']['title']})
    return JsonResponse(json.dumps(results), status=200)
