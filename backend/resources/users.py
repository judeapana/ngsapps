import secrets

from flask import request
from flask_jwt_extended import jwt_required
from flask_restplus import Resource, fields, inputs, Namespace
from flask_restplus.reqparse import RequestParser

from backend import pagination, db
from backend.common import string
from backend.common.schema import UserSchema
from backend.models import User

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
    method_decorators = [jwt_required]

    def get(self):
        return pagination.paginate(User.query, user_schema)

    def post(self):
        args = parser.parse_args(strict=True)
        user = User(**args)
        pwd = secrets.token_hex(5)
        user.set_password(pwd)
        return User.user_exist(args) if User.user_exist(args) else user.save(**args)


class UserResource(Resource):
    method_decorators = [jwt_required]

    @ns_user.marshal_with(user_schema, envelope='data')
    def get(self, pk):
        return User.query.get_or_404(pk)

    def put(self, pk):
        user = User.query.get_or_404(pk)
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
        schema = UserSchema()
        user = schema.load(data=request.json, instance=user, session=db.session, unknown='exclude')
        return user.save(**args), 200

    def delete(self, pk):
        user = User.query.get_or_404(pk)
        return user.delete(), 202


ns_user.add_resource(UserResourceList, '/users', endpoint='users')
ns_user.add_resource(UserResource, '/user/<int:pk>', endpoint='user')
