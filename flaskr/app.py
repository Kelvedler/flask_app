from flask import Flask

from config import config
from db import engine
from common.api import BadRequest
from main.views import api as main_api


if __name__ == '__main__':

    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(main_api)

    app.register_error_handler(400, BadRequest().as_error_handler)

    engine.connect()

    app.run()
