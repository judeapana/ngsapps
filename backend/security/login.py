from datetime import datetime

from flask import request, current_app
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, get_jti, jwt_refresh_token_required, \
    get_jwt_identity
from flask_restplus import Resource
from flask_restplus.reqparse import RequestParser

from backend import redis
from backend.common.constants import LOGIN_NOTIFY
from backend.models import User
from backend.security import auth
from backend.tasks.mail import send_mail_rq


@auth.route('/')
class Login(Resource):
    def post(self):
        parser = RequestParser(bundle_errors=True)
        parser.add_argument('username', type=str, required=True, location='json', help='username is required')
        parser.add_argument('password', type=str, required=True, location='json', help='password is required')
        args = parser.parse_args(strict=True)
        user = User.query.filter((User.username == args.username) | (User.email == args.username)).first()
        if not user:
            return {'message': 'Incorrect username or password'}, 401
        else:
            if not check_password_hash(user.password, args.password):
                return {'message': 'Incorrect username or password'}, 401
            else:
                if not user.status:
                    return {'message': 'Your account is currently inactive'}, 401
                else:
                    send_mail_rq.queue(LOGIN_NOTIFY.format(name=user.full_name, app_name='Ngsapps', email=user.email,
                                                           time=str(datetime.utcnow()), ip=request.remote_addr,
                                                           user_agent=request.user_agent), [user.email],
                                       'Ngsapp Support')
                    # create JWT
                    access_token = create_access_token(identity=str(user.uuid))
                    refresh_token = create_refresh_token(identity=str(user.uuid))

                    access_jti = get_jti(encoded_token=access_token)
                    refresh_jti = get_jti(encoded_token=refresh_token)
                    redis.set(access_jti, 'false', current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] * 1.2)
                    redis.set(refresh_jti, 'false', current_app.config['JWT_REFRESH_TOKEN_EXPIRES'] * 1.2)
                    return {'access_token': access_token, 'refresh_token': refresh_token}, 200


@auth.route('/refresh')
class Refresh(Resource):
    method_decorators = [jwt_refresh_token_required]

    def post(self):
        parser = RequestParser(bundle_errors=True)
        parser.add_argument('username', type=str, required=True, location='json', help='username is required')
        parser.add_argument('password', type=str, required=True, location='json', help='password is required')
        args = parser.parse_args(strict=True)
        user = User.query.filter((User.username == args.username) | (User.email == args.username)).first()
        if not user:
            return {'message': 'Incorrect username or password'}, 401
        else:
            if not check_password_hash(user.password, args.password):
                return {'message': 'Incorrect username or password'}, 401
            else:
                if not user.status:
                    return {'message': 'Your account is currently inactive'}, 401
                else:
                    current_user = get_jwt_identity()
                    access_token = create_access_token(identity=current_user)
                    access_jti = get_jti(encoded_token=access_token)
                    redis.set(access_jti, 'false', current_app.config['JWT_ACCESS_TOKEN_EXPIRES'] * 1.2)
                    return {'access_token': access_token}, 201
