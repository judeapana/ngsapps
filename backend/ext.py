from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_rest_paginate import Pagination
from flask_rq2 import RQ
from flask_sqlalchemy import SQLAlchemy

jwt = JWTManager()
db = SQLAlchemy()
rq = RQ()
mail = Mail()
migrate = Migrate()
ma = Marshmallow()
bcrypt = Bcrypt()
pagination = Pagination()
cors = CORS()
