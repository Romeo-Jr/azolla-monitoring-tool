from flask import Blueprint

main = Blueprint('main', __name__)
err = Blueprint('err', __name__)
auth = Blueprint('auth', __name__)
api = Blueprint('api', __name__, url_prefix='/api')

from . import routes, errors, authentication, api_module