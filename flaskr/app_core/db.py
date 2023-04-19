from sqlalchemy import create_engine

from app_core.config import config

engine = create_engine(config.DATABASE_URI)


def label_columns(table):
    return [column.label(f'{column.table.description}__{column.description}') for column in table.columns]
