import secrets

import werkzeug
from flask import request, url_for
from flask_jwt_extended import jwt_required, current_user
from flask_restplus import Resource, fields, inputs, Namespace, abort
from flask_restplus.reqparse import RequestParser
from werkzeug.security import safe_str_cmp

from backend.common import string
from backend.common.constants import CHANGE_EMAIL, NEW_ACC
from backend.common.schema import UserSchema
from backend.ext import pagination, db, bcrypt
from backend.models import User
from backend.tasks.mail import send_mail_rq
from backend.utils import roles_required, img_upload

ns_user = Namespace('user', 'User management users/admin/client/team members')
user_schema = ns_user.model('User', {
    'id': fields.Integer(),
    'username': fields.String(min_length=4, max_length=3),
    'email': fields.String(),
    'status': fields.Boolean(),
    'full_name': fields.String(),
    'gender': fields.String(),
    'role': fields.String(),
    'confirmed': fields.Boolean(),
    'created': fields.DateTime('rfc822'),
})
schema = UserSchema()

parser = RequestParser(trim=True, bundle_errors=True)
parser.add_argument('full_name', required=True, type=string, location='json')
parser.add_argument('username', required=True, type=string, location='json')
parser.add_argument('email', required=True, type=inputs.email(), help='Email address is required',
                    location='json')
parser.add_argument('gender', required=True, type=str, choices=['Male', 'Female', 'Others'],
                    help='Gender is required', location='json')
parser.add_argument('role', required=True, type=str, choices=['ADMIN', 'TEAM_MEMBER', 'CLIENT', 'USER'],
                    help='User must have a role', location='json')
parser.add_argument('status', required=False, type=inputs.boolean, location='json')
parser.add_argument('confirmed', required=False, type=inputs.boolean, location='json')


class UserResourceList(Resource):
    method_decorators = [roles_required(['ADMIN',]), jwt_required]

    def get(self):
        return pagination.paginate(User, schema, True)

    def post(self):
        args = parser.parse_args(strict=True)
        user = User(**args)
        pwd = secrets.token_hex(5)
        user.set_password(pwd)
        user.confirmed = True
        send_mail_rq.queue(NEW_ACC.format(username=user.username, password=pwd, ), [args.email],
                           'Welcome')
        return User.user_exist(args) if User.user_exist(args) else user.save(**args)


class UserResource(Resource):
    method_decorators = [roles_required(['ADMIN']), jwt_required]

    @ns_user.marshal_with(user_schema, envelope='data')
    def get(self, pk):
        return User.query.filter(User.id == pk, User.role != 'ADMIN').first_or_404()

    def put(self, pk):
        user = User.query.filter(User.id == pk, User.role != 'ADMIN').first_or_404()
        args = parser.parse_args(strict=True)
        check_mail = User.query.filter(User.email == args.email, User.id != user.id).first()
        check_username = User.query.filter(User.username == args.username, User.id != user.id).first()
        r = {'errors': {}}
        if check_username:
            r.get('errors').update({'username': 'username already exist'})
        if check_mail:
            r.get('errors').update({'email_address': 'email address already exist'})
        if r.get('errors'):
            return r, 400
        user = schema.load(data=request.json, instance=user, session=db.session, unknown='exclude')
        return user.save(**args), 200

    def delete(self, pk):
        user = User.query.filter(User.id == pk, User.role != 'ADMIN').first_or_404()
        return user.delete(), 202


class UserProfileResource(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER', 'CLIENT', 'TEAM_MEMBER']), jwt_required]

    def put(self, option):
        profile_parser = RequestParser(trim=True, bundle_errors=True)
        if option == 'general':
            profile_parser.add_argument('username', required=True, type=string, location='json')
            profile_parser.add_argument('full_name', required=True, type=string, location='json')
            profile_parser.add_argument('gender', required=True, type=str, choices=['Male', 'Female', 'Others'],
                                        help='Gender is required', location='json')
            args = profile_parser.parse_args(strict=True)
            if User.query.filter(User.username == args.username, User.id != current_user.id).first():
                return {'message': 'Username already exist, please use different one'}, 400
            current_user.full_name = args.full_name
            current_user.gender = args.gender
            return current_user.save(**args)

        if option == 'pwd':
            profile_parser.add_argument('old_pwd', required=True, type=str, location='json')
            profile_parser.add_argument('new_pwd', type=inputs.regex('[A-Za-z0-9@#$%^&+=]{8,}'),
                                        required=True, location='json',
                                        help='Password must have a minimum of eight characters.')
            profile_parser.add_argument('confirm_pwd', type=inputs.regex('[A-Za-z0-9@#$%^&+=]{8,}'),
                                        required=True, location='json',
                                        help='Password must have a minimum of eight characters.')
            args = profile_parser.parse_args(strict=True)
            if not bcrypt.check_password_hash(current_user.password, args.old_pwd):
                return {'message': 'Old password doesnt match current password'}, 400
            if not safe_str_cmp(args.confirm_pwd, args.new_pwd):
                return {"message": 'passwords dont match'}
            current_user.password = bcrypt.generate_password_hash(args.new_pwd).decode()
            current_user.save()
            send_mail_rq.queue('Your password was changed!', [current_user.email],
                               'Password Changed')
            return {'message': 'Your password has been updated successfully'}
        if option == 'email':
            profile_parser.add_argument('pwd', required=True, type=str, location='json')
            profile_parser.add_argument('old_email', required=True, type=inputs.email(),
                                        help='Email address is required',
                                        location='json')
            profile_parser.add_argument('new_email', required=True, type=inputs.email(),
                                        help='Email address is required',
                                        location='json')
            args = profile_parser.parse_args(strict=True)
            if not bcrypt.check_password_hash(current_user.password, args.pwd):
                return abort(401)
            token = current_user.create_token(payload={'email': args.new_email})
            url = url_for('api.auth_change_email', token=token, _external=True)
            send_mail_rq.queue(CHANGE_EMAIL.format(name=current_user.full_name, url=url), [args.new_email],
                               'Change Email')
            return {'message': 'Email has been sent'}
        if option == 'img':
            profile_parser.add_argument('files', required=True, location='files',
                                        type=werkzeug.datastructures.FileStorage)
            args = profile_parser.parse_args(strict=True)
            file = img_upload(args.file)
            if file.get('message'):
                return file, 400
            current_user.img = file.get('filename')
            file.get('upload').save(file.get('full_path'))
            return current_user.save(filename=current_user.img), 201
        return abort(404)


ns_user.add_resource(UserResourceList, '/', endpoint='users')
ns_user.add_resource(UserResource, '/<int:pk>', endpoint='user')
ns_user.add_resource(UserProfileResource, '/profile/<string:option>', endpoint='user_profile')
