from elastic_migrations.base import Migration
from app_core.elastic import client

POSTS = 'posts'


def forwards():
    settings = {
        'index.number_of_replicas': 0
    }
    client.indices.put_settings(settings=settings, index=POSTS)


def reverse():
    settings = {
        'index.number_of_replicas': 1
    }
    client.indices.put_settings(settings=settings, index=POSTS)


migration = Migration(
    depends_on='0002_vector_logger',
    forwards=forwards,
    reverse=reverse
)
