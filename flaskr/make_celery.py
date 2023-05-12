from app import create_app
from main.tasks import beat_schedule as main_beat_schedule

flask_app = create_app()
celery_app = flask_app.extensions['celery']

celery_app.autodiscover_tasks(['main.tasks'])

celery_app.conf.beat_schedule = {
    **main_beat_schedule
}
