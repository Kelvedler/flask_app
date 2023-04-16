from marshmallow import fields, validate, pre_dump
from sqlalchemy import Table, Column, String, UUID, ForeignKey

from main.models.base import metadata_obj, get_base_columns, BaseSchema

post_table = Table(
    'post',
    metadata_obj,
    *get_base_columns(),
    Column('person', UUID, ForeignKey('person.id'), nullable=False),
    Column('title', String(150), nullable=False),
    Column('text', String(1000), nullable=False),
)


class PostSchema(BaseSchema):
    person = fields.Nested('PersonSchema', dump_only=True)
    title = fields.String(validate=validate.Length(min=5, max=150), required=True)
    text = fields.String(validate=validate.Length(min=10, max=1000), required=True)


class PostSchemaFromFlat(PostSchema):
    @pre_dump
    def from_flat(self, data, **kwargs):
        unflattened_data = {}
        person_object = {}
        for key, value in data.items():
            post_prefix, person_prefix = 'post__', 'person__'
            if key.startswith(post_prefix):
                unflattened_data[key[len(post_prefix):]] = value
            elif key.startswith(person_prefix):
                person_object[key[len(person_prefix):]] = value
        unflattened_data['person'] = person_object
        return unflattened_data


post_comment_table = Table(
    'post_comment',
    metadata_obj,
    *get_base_columns(),
    Column('post', UUID, ForeignKey('post.id'), nullable=False),
    Column('person', UUID, ForeignKey('person.id'), nullable=False),
    Column('text', String(250), nullable=False),
)
