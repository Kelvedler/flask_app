from flask import Blueprint

from .multiple import multiple
from .titles import titles
from .single import single

posts = Blueprint('posts', __name__, url_prefix='posts/')

posts.register_blueprint(multiple)
posts.register_blueprint(titles)
posts.register_blueprint(single)
