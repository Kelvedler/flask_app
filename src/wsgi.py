import logging
from app import create_app

gunicorn_access = logging.getLogger('gunicorn.access')
gunicorn_error = logging.getLogger('gunicorn.error')
app = create_app()
app.logger.addHandler(gunicorn_access)
app.logger.addHandler(gunicorn_error)
