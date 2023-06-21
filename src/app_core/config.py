import os
from datetime import timedelta
from dotenv import load_dotenv
from app_core.constants import BASE_DIR

load_dotenv()


class Config:
    CONSOLE_LOG_LEVEL = os.getenv('CONSOLE_LOG_LEVEL', default='INFO')
    SYSTEM_LOG_LEVEL = os.getenv('SYSTEM_LOG_LEVEL', default='INFO')
    DEBUG = False
    DATABASE_URI = os.getenv('DATABASE_URI')
    ELASTICSEARCH = {
        'URI': os.getenv('ELASTICSEARCH_URI'),
        'PASSWORD': os.getenv('ELASTICSEARCH_PASSWORD')
    }
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = os.getenv('REDIS_PORT')
    CELERY = {
        'broker_url': f'redis://{REDIS_HOST}:{REDIS_PORT}',
        'result_backend': f'redis://{REDIS_HOST}:{REDIS_PORT}',
        'task_ignore_result': True
    }

    WEBSOCKETS_HOST = os.getenv('WEBSOCKETS_HOST')
    WEBSOCKETS_PORT = os.getenv('WEBSOCKETS_PORT')
    AMQP_URL = os.getenv('AMQP_URL')

    LOGGING_DICT = {
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
                'level': CONSOLE_LOG_LEVEL,
                'class': 'logging.StreamHandler',
                'formatter': 'brief'
            },
            'general_file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'brief',
                'filename': f'{BASE_DIR}/logs/general.log',
                'maxBytes': 1000000,
                'backupCount': 10
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'default',
                'filename': f'{BASE_DIR}/logs/error.log',
                'maxBytes': 1000000,
                'backupCount': 10
            }
        },
        'root': {
            'handlers': ['console', 'general_file', 'error_file']
        },
        'loggers': {
            'app': {
                'handlers': ['console', 'general_file', 'error_file'],
                'level': SYSTEM_LOG_LEVEL,
                'propagate': False
            },
            'main': {
                'handlers': ['console', 'general_file', 'error_file'],
                'level': SYSTEM_LOG_LEVEL,
                'propagate': False
            },
            'web_sockets': {
                'handlers': ['console', 'general_file', 'error_file'],
                'level': SYSTEM_LOG_LEVEL,
                'propagate': False
            },
        },
    }


class DevelopmentConfig(Config):
    SECRET_KEY = 'mZq4t7w!z%C*F-JaNdRgUkXn2r5u8x/A'
    JWT_ACCESS_EXPIRATION_TIMEDELTA = timedelta(days=30)
    JWT_REFRESH_EXPIRATION_TIMEDELTA = timedelta(days=364)


class ProductionConfig(Config):
    SECRET_KEY = os.getenv('SECRET_KEY')
    JWT_ACCESS_EXPIRATION_TIMEDELTA = timedelta(minutes=5)
    JWT_REFRESH_EXPIRATION_TIMEDELTA = timedelta(days=14)


_config_options = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

config = _config_options.get(os.getenv('CONFIG') or 'development')
