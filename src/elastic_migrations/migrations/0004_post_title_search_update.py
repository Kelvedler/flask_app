from elasticsearch.helpers import bulk
from sqlalchemy import select

from app_core.db import engine, label_columns
from app_core.elastic import client
from main.models.post import post_table
from main.models.person import person_table
from elastic_migrations.base import Migration

POSTS = 'posts'
POSTS_NEW = f'{POSTS}-000001'


def get_posts():
    with engine.connect() as conn:
        return conn.execute(select(
            *label_columns(post_table), *label_columns(person_table)
        ).where(post_table.c.person == person_table.c.id)).all()


def index_posts_with_legacy_mapping(posts, index_name):
    actions = []
    for post in posts:
        post_dict = post._asdict()
        post_title = post_dict['post__title']
        actions.append({
            '_id': post_dict['post__id'],
            'title': post_title,
            'title_suggest': post_title.split(),
            'text': post_dict['post__text'],
            'person_id': post_dict['person__id'],
            'person_name': post_dict['person__name']
        })
    return bulk(client, actions, index=index_name)


def index_posts_with_current_mapping(posts, index_name):
    actions = []
    for post in posts:
        post_dict = post._asdict()
        post_title = post_dict['post__title']
        actions.append({
            '_id': post_dict['post__id'],
            'title': post_title,
            'title_search_as_type': post_title,
            'text': post_dict['post__text'],
            'person_id': post_dict['person__id'],
            'person_name': post_dict['person__name']
        })
    return bulk(client, actions, index=index_name)


def forwards():
    posts = get_posts()

    mapping = {
        'properties': {
            'title': {'type': 'keyword',
                      'ignore_above': 30},
            'title_search_as_type': {'type': 'search_as_you_type'},
            'text': {
                'type': 'text',
                'analyzer': 'whitespace'
            },
            'person_id': {'type': 'keyword'},
            'person_name': {'type': 'keyword',
                            'ignore_above': 30}
        }
    }
    settings = {
        'index.number_of_replicas': 0
    }
    aliases = {
        POSTS: {
            'is_write_index': True
        }
    }
    client.indices.delete(index=POSTS)
    client.indices.put_template(mappings=mapping, settings=settings, index_patterns=f'{POSTS}-*',
                                name=POSTS)
    client.indices.create(index=POSTS_NEW, aliases=aliases)
    _, errs = index_posts_with_current_mapping(posts, POSTS_NEW)
    if errs:
        _, errs = index_posts_with_legacy_mapping(posts, POSTS)
        if errs:
            raise Exception('failed to apply, failed to reverse')
        raise Exception('failed to apply')


def reverse():
    client.indices.delete_template(name=POSTS)
    client.indices.delete(index=POSTS_NEW)
    posts = get_posts()
    _, errs = index_posts_with_legacy_mapping(posts, POSTS)
    if errs:
        raise Exception('failed to apply')


migration = Migration(
    depends_on='0003_posts_settings',
    forwards=forwards,
    reverse=reverse
)
