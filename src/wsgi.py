import logging
from app import create_app

app = create_app()
gunicorn_logger = logging.getLogger('gunicorn.access')
app.logger.handlers = gunicorn_logger.handlers
