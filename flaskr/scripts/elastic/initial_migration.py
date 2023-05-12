from elasticsearch.helpers import bulk
from sqlalchemy import select

from app_core.db import engine, label_columns
from app_core.elastic import client
from main.models.post import post_table
from main.models.person import person_table

POSTS = 'posts'


def forwards():
    with engine.connect() as conn:
        posts = conn.execute(select(
            *label_columns(post_table), *label_columns(person_table)
        ).where(post_table.c.person == person_table.c.id)).all()
    mapping = {
        'properties': {
            'title': {'type': 'keyword',
                      'ignore_above': 30},
            'title_suggest': {'type': 'completion'},
            'text': {
                'type': 'text',
                'analyzer': 'whitespace'
            },
            'person_id': {'type': 'keyword'},
            'person_name': {'type': 'keyword',
                            'ignore_above': 30}
        }
    }
    client.indices.create(index=POSTS, mappings=mapping)
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
    success, errs = bulk(client, actions, index=POSTS)
    print(f'success: {success}')
    print('errors:')
    for err in errs:
        print(f'\t{err}')


def reverse():
    client.indices.delete(index=POSTS)


if __name__ == '__main__':
    forwards()
