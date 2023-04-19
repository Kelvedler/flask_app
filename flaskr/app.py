from logging.config import dictConfig
from flask import Flask

from app_core.api import BadRequest, ServerInternalError
from app_core.config import config
from app_core.db import engine
from main.views import api as main_api


if __name__ == '__main__':
    dictConfig({
        'version': 1,
        'disable_existing_loggers': True,
        'formatters': {
            'brief': {
                'format': '%(asctime)s: %(levelname)s %(message)s'
            },
            'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
            }
        },
        'handlers': {
            'console': {
                'level': config.CONSOLE_LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'brief'
            },
            'general_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'brief',
                'filename': 'logs/general.log',
                'maxBytes': 1000000,
                'backupCount': 10
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': 'logs/error.log',
                'maxBytes': 1000000,
                'backupCount': 10
            }
        },
        'root': {
            'handlers': ['console', 'general_file', 'error_file']
        },
        'loggers': {
            'main': {
                'handlers': ['console', 'general_file', 'error_file'],
                'level': config.SYSTEM_LOG_LEVEL,
                'propagate': False
            }
        }
    })

    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(main_api)

    app.register_error_handler(400, BadRequest().as_error_handler)
    app.register_error_handler(500, ServerInternalError().as_error_handler)

    engine.connect()

    app.run()
