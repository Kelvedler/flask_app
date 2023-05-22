import json
import pika


def broadcast_comment(comment, event):
    body = json.dumps({
        'event': event,
        'payload': json.loads(comment)
    })
    connection = pika.BlockingConnection(pika.ConnectionParameters('127.0.0.1'))
    comments_channel = connection.channel()
    comments_channel.queue_declare(queue='broadcast', auto_delete=True)
    comments_channel.basic_publish(exchange='message', routing_key='broadcast', body=body)
    connection.close()
