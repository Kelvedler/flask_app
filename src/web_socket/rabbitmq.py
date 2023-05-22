import asyncio
import functools
import json
import pika
from pika.adapters.asyncio_connection import AsyncioConnection
from pika.exchange_type import ExchangeType


class Consumer:
    EXCHANGE = 'message'
    EXCHANGE_TYPE = ExchangeType.topic
    QUEUE = 'broadcast'
    ROUTING_KEY = 'broadcast'

    def __init__(self, amqp_url, on_message_callback):
        self.should_reconnect = False
        self.was_consuming = False

        self._connection = None
        self._channel = None
        self._closing = False
        self._consumer_tag = None
        self._consuming = False
        self._prefetch_count = 1
        self._url = amqp_url
        self.on_message_callback = on_message_callback

    def connect(self):
        self._connection = AsyncioConnection(
            parameters=pika.URLParameters(self._url),
            on_open_callback=self.on_connection_open,
            on_open_error_callback=self.on_connection_open_error,
            on_close_callback=self.on_connection_closed
        )

    async def connection(self):
        while True:
            await asyncio.sleep(1)
            return self._connection

    def on_connection_open(self, _unused_connection):
        self.open_channel()

    def on_connection_open_error(self, _unused_connection, err):
        self.reconnect()

    def reconnect(self):
        self.should_reconnect = True
        self.stop()

    def stop(self):
        if not self._closing:
            self._closing = True
            if self._consuming:
                self.stop_consuming()

    def stop_consuming(self):
        if self._channel:
            self._channel.basic_cancel(self._consumer_tag, self.on_cancel_ok)

    def on_cancel_ok(self, _unused_frame):
        self._consuming = False
        self.close_channel()

    def close_channel(self):
        self._channel.close()

    def on_connection_closed(self, _unused_connection, reason):
        self._channel = None
        if self._closing:
            self._connection.ioloop.stop()
        else:
            self.reconnect()

    def open_channel(self):
        self._connection.channel(on_open_callback=self.on_channel_open)

    def on_channel_open(self, channel):
        self._channel = channel
        self.add_on_channel_close_callback()
        self.setup_exchange(self.EXCHANGE)

    def add_on_channel_close_callback(self):
        self._channel.add_on_close_callback(self.on_channel_closed)

    def on_channel_closed(self, channel, reason):
        self.close_connection()

    def close_connection(self):
        self._consuming = False
        if not self._connection.is_closing and not self._connection.is_closed:
            self._connection.close()

    def setup_exchange(self, exchange_name):
        self._channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=self.EXCHANGE_TYPE,
            callback=self.on_exchange_declare_ok
        )

    def on_exchange_declare_ok(self, _unused_frame):
        self.setup_queue(self.QUEUE)

    def setup_queue(self, queue_name):
        callback = functools.partial(self.on_queue_declare_ok, queue_name=queue_name)
        self._channel.queue_declare(queue=queue_name, callback=callback, auto_delete=True)

    def on_queue_declare_ok(self, _unused_frame, queue_name):
        self._channel.queue_bind(
            queue_name,
            self.EXCHANGE,
            routing_key=self.ROUTING_KEY,
            callback=self.on_bind_ok)

    def on_bind_ok(self, _unused_frame):
        self.set_qos()

    def set_qos(self):
        self._channel.basic_qos(prefetch_count=self._prefetch_count, callback=self.on_basic_qos_ok)

    def on_basic_qos_ok(self, _unused_frame):
        self.start_consuming()

    def start_consuming(self):
        self.add_on_cancel_callback()
        self._consumer_tag = self._channel.basic_consume(self.QUEUE, self.on_message)
        self.was_consuming = True
        self._consuming = True

    def add_on_cancel_callback(self):
        self._channel.add_on_cancel_callback(self.on_consumer_canceled)

    def on_consumer_canceled(self, method_frame):
        if self._channel:
            self._channel.close()

    def on_message(self, _unused_channel, basic_deliver, properties, body):
        self.acknowledge_message(basic_deliver.delivery_tag)
        self.on_message_callback(message=json.loads(body.decode('utf-8')))

    def acknowledge_message(self, delivery_tag):
        self._channel.basic_ack(delivery_tag)
