import os
from elasticsearch import Elasticsearch

from app_core.config import config
from app_core.constants import BASE_DIR

client = Elasticsearch(
    config.ELASTICSEARCH['URI'],
    ca_certs=os.path.join(BASE_DIR, 'ca.crt'),
    basic_auth=('elastic', config.ELASTICSEARCH['PASSWORD'])
)
