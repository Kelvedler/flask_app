from datetime import datetime, timezone
from math import ceil


def get_now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)


def get_now_ts():
    return ceil(datetime.utcnow().replace(tzinfo=timezone.utc).timestamp())


def to_ts(dt: datetime):
    return ceil(dt.timestamp())
