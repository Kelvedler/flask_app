import os
from elasticsearch import Elasticsearch

from app_core.config import config
from app_core.constants import BASE_DIR
from app_core.redis_ import client as redis_client

client = Elasticsearch(
    config.ELASTICSEARCH['URI'],
    ca_certs=os.path.join(BASE_DIR, 'ca.crt'),
    basic_auth=('elastic', config.ELASTICSEARCH['PASSWORD']),
    max_retries=5,
)


class UpdateQueue:

    def __init__(self, prefix):
        self.redis_client = redis_client
        self.key = f'es_queue_{prefix}'

    def add_objects(self, *object_id):
        self.redis_client.sadd(self.key, *[str(id_) for id_ in object_id])

    def remove_objects(self, *object_id):
        self.redis_client.srem(self.key, *[str(id_) for id_ in object_id])

    def get_objects(self):
        return [element.decode("utf-8") for element in self.redis_client.smembers(self.key)]
