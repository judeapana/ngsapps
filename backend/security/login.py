from flask import jsonify
from flask_bcrypt import check_password_hash
from flask_jwt_extended import create_access_token
from flask_restplus import Resource
from flask_restplus.reqparse import RequestParser

from backend.models import User


class LoginResource(Resource):
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
                    access_token = create_access_token(identity=str(user.uuid))
                    return {'access_token': access_token}, 200
