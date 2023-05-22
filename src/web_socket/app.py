import asyncio
import os
import sys
from rabbitmq import Consumer
from websocket import Server

from app_core.config import config


def run():
    server = Server(config.WEBSOCKETS_HOST, config.WEBSOCKETS_PORT)
    consumer = Consumer(amqp_url=config.AMQP_URL, on_message_callback=server.broadcast)
    consumer.connect()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(server.serve)
    asyncio.ensure_future(consumer.connection())
    loop.run_forever()


if __name__ == '__main__':
    try:
        run()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(130)
        except SystemExit:
            os._exit(130)
