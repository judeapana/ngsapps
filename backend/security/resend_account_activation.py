from flask import jsonify, url_for
from flask_restful.reqparse import RequestParser
from flask_restplus import Resource
from flask_restplus import inputs

from backend.models import User
from backend.tasks.mail import send_mail_rq


class ResendAccountActivationResource(Resource):
    def post(self):
        parser = RequestParser(bundle_errors=True)
        parser.add_argument('email_address', type=inputs.email(), required=True, location='json')
        args = parser.parse_args(strict=True)
        user = User.query.filter(User.email == args.email_address).first()
        if not user:
            return jsonify(message='Please account is not found')
        if user.status:
            return jsonify(message='Your dont have access to this function')
        token = user.create_token()
        message = f"""Your account activation link <a href='{url_for('api.confirm', token=token, _external=True)}'> Click here</a>"""
        send_mail_rq.queue(user.email, message, 'Resend Account Activation')
        return jsonify(message='Account reset link has been sent')
