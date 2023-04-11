from sqlalchemy import Table, Column, String, UUID, ForeignKey
from main.models.base import metadata_obj, base_columns

post_table = Table(
    'post',
    metadata_obj,
    *base_columns,
    Column('person', UUID, ForeignKey('person.id'), nullable=False),
    Column('text', String(1000), nullable=False)
)

post_comment_table = Table(
    'post_comment',
    metadata_obj,
    *base_columns,
    Column('post', UUID, ForeignKey('post.id'), nullable=False),
    Column('person', UUID, ForeignKey('person.id'), nullable=False),
    Column('text', String(250), nullable=False)
)
