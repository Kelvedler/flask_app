import uuid
from sqlalchemy import Column, UUID, TIMESTAMP, MetaData
from sqlalchemy.sql import func

metadata_obj = MetaData()

base_columns = (
    Column('id', UUID(as_uuid=True), default=uuid.uuid4, primary_key=True),
    Column('created_at', TIMESTAMP(timezone=True), default=func.timezone('UTC', func.current_timestamp()), nullable=False),
    Column('updated_at', TIMESTAMP(timezone=True), default=func.timezone('UTC', func.current_timestamp()),
           onupdate=func.timezone('UTC', func.current_timestamp()), nullable=False)

)
