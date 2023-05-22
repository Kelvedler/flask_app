import json
import pika

from app_core.config import config


def broadcast_comment(comment, event):
    body = json.dumps({
        'event': event,
        'payload': json.loads(comment)
    })
    connection = pika.BlockingConnection(pika.URLParameters(config.AMQP_URL))
    comments_channel = connection.channel()
    comments_channel.queue_declare(queue='broadcast', auto_delete=True)
    comments_channel.basic_publish(exchange='message', routing_key='broadcast', body=body)
    connection.close()
