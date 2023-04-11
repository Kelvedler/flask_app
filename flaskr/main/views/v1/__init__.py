from flask import Blueprint

from .sign_up import sign_up
from .sign_in import sign_in
from .me import me
from .refresh import refresh

v1 = Blueprint('v1/', __name__, url_prefix='v1/')

v1.register_blueprint(sign_up)
v1.register_blueprint(sign_in)
v1.register_blueprint(me)
v1.register_blueprint(refresh)
