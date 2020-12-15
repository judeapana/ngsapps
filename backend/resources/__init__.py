from flask import Blueprint
from flask_restplus import Api

bapi = Blueprint('api', __name__, url_prefix='/api')
api = Api(bapi)
