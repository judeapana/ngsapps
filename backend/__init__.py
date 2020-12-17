from uuid import UUID

from flask import Flask

from backend.config import DevelopmentConfig
from backend.ext import cors, db, pagination, bcrypt, migrate, rq, ma, mail, jwt, redis
from backend.models import User


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    pagination.init_app(app, db)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    rq.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    app.register_blueprint(bapi)
    redis.init_app(app)

    @jwt.user_loader_callback_loader
    def load_user(identity):
        return User.query.filter(User.uuid == UUID(identity)).one()

    @jwt.token_in_blacklist_loader
    def blacklist(decrypted_token):
        jti = decrypted_token['jti']
        entry = redis.get(jti)
        try:
            if entry is None:
                return True
            return entry.decode() == 'true'
        except:
            return True

    # with app.app_context():
    #     urlvars = False  # Build query strings in URLs
    #     swagger = True  # Export Swagger specifications
    #     data = api.as_postman(urlvars=urlvars, swagger=swagger)
    #     file = open('file.json', '+w')
    #     file.write(json.dumps(data))

    return app


from backend.api.apiv1 import bapi
