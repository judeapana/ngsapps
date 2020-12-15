from uuid import UUID

from flask import jsonify
from flask_restful.reqparse import RequestParser
from flask_restplus import Resource

from backend.models import User


class ConfirmAccountResource(Resource):
    def get(self):
        parser = RequestParser(bundle_errors=True, trim=True)
        parser.add_argument('token', type=str, required=True, location='args', help='Token is missing')
        args = parser.parse_args(strict=True)
        token = User.authenticate_token(args.token)
        if not token:
            return jsonify(message='Token is invalid or has expired', other='please generate a new one')
        user = User.query.filter(User.uuid == UUID(token.get('id'))).first_or_404()
        if user.confirmed:
            return jsonify(message='Your account is already confirmed')
        user.confirmed = True
        user.save()
        return jsonify(message='your account has been successfully activated')
