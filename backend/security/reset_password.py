from uuid import UUID

from flask_bcrypt import generate_password_hash
from flask_restful.reqparse import RequestParser
from flask_restplus import Resource
from flask_restplus import inputs
from werkzeug.security import safe_str_cmp

from backend.models import User
from backend.security import auth


@auth.route('/reset-pwd')
class ResetPassword(Resource):
    parser = RequestParser(bundle_errors=True)

    def get(self):
        ResetPassword.parser.add_argument('token', type=str, required=True, location='args',
                                          help='Token is missing')
        args = ResetPassword.parser.parse_args(strict=True)
        token = User.authenticate_token(args.token)
        if not token:
            return {'message': 'Token is invalid or has expired', "other": 'Please regenerate token'}
        return {'message': 'Token is valid'}

    def put(self):
        ResetPassword.parser.add_argument('token', type=str, required=True, location='args',
                                          help='Token is missing')
        ResetPassword.parser.add_argument('new_pwd', type=inputs.regex('[A-Za-z0-9@#$%^&+=]{8,}'),
                                          required=True, location='json',
                                          help='Password must have a minimum of eight characters.')
        ResetPassword.parser.add_argument('confirm_pwd', type=inputs.regex('[A-Za-z0-9@#$%^&+=]{8,}'),
                                          required=True, location='json',
                                          help='Password must have a minimum of eight characters.')
        args = ResetPassword.parser.parse_args(strict=True)

        token = User.authenticate_token(args.token)
        if not token:
            return {'message': 'Token is invalid or has expired', "other": 'Please regenerate token'}
        try:
            if not safe_str_cmp(args.confirm_pwd, args.new_pwd):
                return {"message": 'passwords dont match'}
            user = User.query.filter(User.uuid == UUID(token.get('id'))).first()
            user.password = generate_password_hash(args.new_pwd).decode()
            user.save()
            return {'message': 'Your password has been updated successfully'}
        except Exception:
            return {'message': 'Something went wrong', 'other': 'unable to update password'}
