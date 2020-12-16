from flask import jsonify, url_for
from flask_restful.reqparse import RequestParser
from flask_restplus import Resource
from flask_restplus import inputs

from backend.models import User
from backend.security import auth
from backend.tasks.mail import send_mail_rq


@auth.route('/forgot-pwd')
class ForgotPassword(Resource):
    def post(self):
        parser = RequestParser()
        parser.add_argument('email_address', type=inputs.email(), required=True, location='json')
        args = parser.parse_args(strict=True)
        user = User.query.filter(User.email == args.email_address).first()
        if not user:
            return jsonify(message='Sorry, your email was not found', other='Check and try again')
        token = user.create_token()
        message = f"""Your reset password link is <a href='{url_for('api.auth_reset_password', token=token, _external=True)}'> 
        Click here</a> """
        send_mail_rq.queue(user.email, message, 'Forgot Password')
        return jsonify(message='A reset link has been sent to your email')
