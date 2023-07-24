import logging
import time
from logging.config import dictConfig
from flask import Flask
from pathlib import Path

from app_core.api import BadRequest, ServerInternalError
from app_core.celery_ import celery_init_app
from app_core.config import config
from app_core.db import engine
from app_core.elastic import client as elastic_client
from app_core.redis_ import client as redis_client
from main.views import api as main_api

BASE_DIR = Path(__file__).resolve().parent


def create_app():
    dictConfig(config.LOGGING_DICT)
    logger = logging.getLogger(__name__)
    logger.info('Starting Flask')
    try:
        app = Flask(__name__)

        app.config.from_object(config)
        app.register_blueprint(main_api)

        app.register_error_handler(400, BadRequest().as_error_handler)
        app.register_error_handler(500, ServerInternalError().as_error_handler)

        engine.connect()
        assert redis_client.ping
        assert elastic_client.ping
        celery_init_app(app)

        return app
    except Exception as e:
        logger.exception(f'Failed to create app: {e}')
