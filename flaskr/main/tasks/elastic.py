from celery import shared_task
from celery.schedules import crontab
from elasticsearch.helpers import bulk
from sqlalchemy import select

from app_core.db import engine, label_columns
from app_core.elastic import client
from main.models.post import post_table, post_update_queue, POST_ELASTIC_INDEX, post_to_elastic_object
from main.models.person import person_table


def update_post_index():
    modified_posts = post_update_queue.get_objects()
    posts_memo = modified_posts.copy()
    with engine.connect() as conn:
        posts = conn.execute(select(
            *label_columns(post_table), *label_columns(person_table)
        ).where(post_table.c.id.in_(modified_posts), post_table.c.person == person_table.c.id)).all()
    actions = []
    for post in posts:
        actions.append(post_to_elastic_object(post))
        posts_memo.remove(str(post._asdict()['post__id']))
    for post_id in posts_memo:
        actions.append({
            '_id': post_id,
            '_op_type': 'delete'
        })
    success, errs = bulk(client, actions, index=POST_ELASTIC_INDEX)
    if success == len(modified_posts):
        post_update_queue.remove_objects(*modified_posts)
    else:
        print(errs)  # TODO fix exception handling


@shared_task()
def update_indices():
    update_post_index()


beat_schedule = {
    'update_indices': {
        'task': 'main.tasks.elastic.update_indices',
        'schedule': crontab(minute='*/1')
    }
}
