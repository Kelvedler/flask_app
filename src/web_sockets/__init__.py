import asyncio
import logging
import os
import sys
from logging.config import dictConfig

from app_core.config import config
from app_core.db import engine
from web_sockets.rabbitmq import Consumer
from web_sockets.websocket import Server


def run():
    dictConfig(config.LOGGING_DICT)
    logger = logging.getLogger(__name__)
    logger.info('Starting web sockets')
    try:
        engine.connect()

        server = Server(config.WEBSOCKETS_HOST, config.WEBSOCKETS_PORT)
        consumer = Consumer(amqp_url=config.AMQP_URL, on_message_callback=server.broadcast)
        consumer.connect()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(server.serve)
        asyncio.ensure_future(consumer.connection())
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info('Interrupted')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
    except Exception as e:
        logger.exception(f'An exception has occurred: {e}')


if __name__ == '__main__':
    run()
