import asyncio
import json
import logging
import re
import websockets
from sqlalchemy import select, exc

from app_core.db import engine
from app_core.jwt_ import jwt_access_required_from_value
from app_core.regex import UUID
from main.models.post import post_table
from main.views.v1.posts.comments.multiple import POST_COMMENT_SUBSCRIPTION

logger = logging.getLogger(__name__)

SUCCESS_RESPONSE = 'success'


class Server:

    def __init__(self, host, port):
        self.serve = websockets.serve(self.handler, host, port)
        self.clients = []

    def get_or_create_client(self, websocket):
        for client in self.clients:
            if client.connection == websocket:
                return client
        client = Client(websocket)
        self.clients.append(client)
        return client

    def remove_client(self, websocket):
        self.clients = list(filter(lambda client: client.connection != websocket, self.clients))

    async def connection_handler(self, websocket):
        if websocket.path != '/ws':
            self.remove_client(websocket)
            return
        print(websocket.request_headers)
        logger.info(self.construct_log(websocket, 'Opened websocket'))
        try:
            await websocket.wait_closed()
        finally:
            self.remove_client(websocket)
            logger.info(self.construct_log(websocket, 'Closed websocket'))

    async def consumer_handler(self, client, websocket):
        async for message in websocket:
            response = client.process_message(message)
            await self.send(websocket, response)

    async def handler(self, websocket):
        client = self.get_or_create_client(websocket)
        connection = asyncio.create_task(self.connection_handler(websocket))
        asyncio.ensure_future(self.consumer_handler(client, websocket))
        await connection

    @staticmethod
    async def send(socket, message):
        try:
            await socket.send(message)
        except websockets.ConnectionClosed:
            pass

    def broadcast(self, message):
        event = message['event']
        for client in self.clients:
            if client.is_subscribed(event):
                asyncio.create_task(self.send(client.connection, json.dumps(message)))

    @staticmethod
    def get_header(websocket, name):
        headers = websocket.request_headers.get_all(name)
        return headers[0] if headers else ''

    def construct_log(self, websocket, text):
        x_real_ip = self.get_header(websocket, 'x-real-ip')
        user_agent = self.get_header(websocket, 'user-agent')
        return f'{x_real_ip} - "{text} {websocket.path}" "{user_agent}"'



class Client:
    MAX_SUBSCRIPTIONS = 10

    def __init__(self, connection):
        self.subscription_options = {
            POST_COMMENT_SUBSCRIPTION.format(f'({UUID})'): self.subscribe_post_comment
        }

        self.connection = connection
        self.person_id = None
        self.subscriptions = set()
        self.commands = {
            'sign_in': self.authenticate,
            'subscribe': self.subscribe
        }

    def validate_message(self, message):
        try:
            message = json.loads(message)
            (command, body), = message.items()
        except (json.JSONDecodeError, AttributeError, ValueError):
            return None, None, json.dumps({'errors': ['invalid']})

        if command not in self.commands:
            return None, None, json.dumps({'errors': ['command__not_found']})
        return command, body, None

    def process_message(self, message):
        command, body, err = self.validate_message(message)
        if err:
            return err
        return self.commands[command](body)

    def authenticate(self, access_token):
        person, err = jwt_access_required_from_value(access_token)
        if err:
            return err
        else:
            self.person_id = person['id']
            return SUCCESS_RESPONSE

    def is_subscribed(self, endpoint):
        for subscription in self.subscriptions:
            if endpoint == subscription:
                return True
        return False

    def subscribe(self, endpoint):
        if len(self.subscriptions) >= self.MAX_SUBSCRIPTIONS:
            return json.dumps({'errors': ['subscribe__limit_exceeded']})

        for pattern, option in self.subscription_options.items():
            match = re.fullmatch(pattern, endpoint)
            if match:
                return option(match.group(1))
        return json.dumps({'errors': ['not_found']})

    def subscribe_post_comment(self, post_id):
        try:
            with engine.connect() as conn:
                conn.execute(select(post_table.c.id).where(post_table.c.id == post_id)).one()
        except (exc.NoResultFound, exc.DataError):
            return json.dumps({'errors': ['post__not_found']})
        else:
            self.subscriptions.add(POST_COMMENT_SUBSCRIPTION.format(post_id))
            return SUCCESS_RESPONSE
