from redis import Redis

from app_core.config import config

client = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
