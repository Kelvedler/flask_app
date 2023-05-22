from flask import Blueprint
from .multiple import multiple

comments = Blueprint('comments', __name__, url_prefix='/comments/')
comments.register_blueprint(multiple)
