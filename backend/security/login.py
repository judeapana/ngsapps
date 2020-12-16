from flask import jsonify
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token
from flask_restplus import Resource
from flask_restplus.reqparse import RequestParser

from backend.models import User
from backend.security import auth
from backend.tasks.mail import rq_login_notify


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
                    return jsonify({'message': 'Your account is currently inactive'}), 401
                else:
                    rq_login_notify.queue(user.email)
                    access_token = create_access_token(identity=str(user.uuid))
                    return {'access_token': access_token}, 200
