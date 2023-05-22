import uuid
from marshmallow import Schema, fields, pre_dump
from sqlalchemy import Column, UUID, TIMESTAMP, MetaData
from sqlalchemy.sql import func

metadata_obj = MetaData()


def get_base_columns():
    return (
        Column('id', UUID(as_uuid=True), default=uuid.uuid4, primary_key=True),
        Column('created_at', TIMESTAMP(timezone=True), default=func.timezone('UTC', func.current_timestamp()),
               nullable=False),
        Column('updated_at', TIMESTAMP(timezone=True), default=func.timezone('UTC', func.current_timestamp()),
               onupdate=func.timezone('UTC', func.current_timestamp()), nullable=False)

    )


class BaseSchema(Schema):
    id = fields.UUID(dump_only=True)
    created_at = fields.Integer(dump_only=True)
    updated_at = fields.Integer(dump_only=True)

    @pre_dump
    def to_timestamp(self, data, **kwargs):
        data['created_at'] = data['created_at'].timestamp()
        data['updated_at'] = data['updated_at'].timestamp()
        return data
