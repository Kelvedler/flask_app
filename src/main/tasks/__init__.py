from app_core.celery_ import key_add_prefix
from .elastic import update_indices, beat_schedule as elastic_beat_schedule

beat_schedule = key_add_prefix(__name__, {
    **elastic_beat_schedule
})
