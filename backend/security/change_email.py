from flask_restful.reqparse import RequestParser
from flask_restplus import Resource

from backend import User
from backend.security import auth

parser = RequestParser(bundle_errors=True)


@auth.route('/change-email')
class ChangeEmail(Resource):

    def get(self):
        parser.add_argument('token', type=str, required=True, location='args',
                            help='Token is missing')
        args = parser.parse_args(strict=True)
        token = User.authenticate_token(args.token)
        if not token:
            return {'message': 'Token is invalid or has expired', 'other': 'Please regenerate token'}, 400
        user = User.query.get_or_404(token.get('id'))
        user.email = token.get('email')
        user.save()
        return {'message': 'Your email has been changed'}
