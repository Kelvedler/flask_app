import os
from datetime import timedelta
from dotenv import load_dotenv

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
