from flask import current_app
from flask_jwt_extended import jwt_required, get_raw_jwt
from flask_restplus import Resource

from backend import redis
from backend.security import auth


@auth.route('/logout')
class Logout(Resource):
    method_decorators = [jwt_required]

    def delete(self):
        jti = get_raw_jwt()['jti']
        redis.set(jti, 'true', current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] * 1.2)
        return {"msg": "Access token revoked"}, 200


@auth.route('/revoke/refresh')
class LogoutRefresh(Resource):
    method_decorators = [jwt_required]

    def delete(self):
        jti = get_raw_jwt()['jti']
        redis.set(jti, 'true', current_app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 1.2)
        return {"msg": "Refresh token revoked"}, 200
