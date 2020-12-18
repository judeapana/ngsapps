from flask import request
from flask_jwt_extended import jwt_required
from flask_restplus import Resource, fields, inputs, Namespace
from flask_restplus.reqparse import RequestParser

from backend.common import string
from backend.common.schema import TeamSchema
from backend.ext import pagination, db
from backend.models import Team, User, TeamMember
from backend.resources.users import user_schema
from backend.utils import roles_required

ns_team = Namespace('team', 'Build teams to handle projects')

schema = TeamSchema()
team_schema = ns_team.model('Team', {
    'id': fields.Integer(),
    'name': fields.String(),
    'email_address': fields.String(),
    'description': fields.String(),
    'users': fields.Nested(user_schema),
    'created': fields.DateTime(),
})

parser = RequestParser(trim=True, bundle_errors=True)

parser.add_argument('name', required=True, location='json', type=string, )
parser.add_argument('email_address', required=True, location='json', type=inputs.email(), )
parser.add_argument('description', required=True, location='json', type=string, )


class TeamResource(Resource):
    method_decorators = [roles_required(['ADMIN']), jwt_required]

    @ns_team.marshal_with(team_schema, envelope='data')
    def get(self, pk):
        return Team.query.get(pk)

    def put(self, pk):
        parser.add_argument('members', required=True, location='json', type=list)
        args = parser.parse_args(strict=True)
        team_check = {'errors': {}}
        if Team.query.filter(Team.name == args.name, Team.id != pk).first():
            team_check.get('errors').update({'name': 'Name already exist'})
        for i in args.members:
            if not User.query.filter_by(role='TEAM_MEMBER', id=i).first():
                team_check.get('errors').update({'members': 'Cant find some users with role TEAM_MEMBER'}), 400
        if team_check.get('errors'):
            return team_check, 400
        team = Team.query.get_or_404(pk)
        team.members.delete()
        for i in args.members:
            team.members.append(TeamMember(user_id=i))
        request.json.pop('members')
        obj = schema.load(data=request.json, unknown='exclude', instance=team, session=db.session)
        return obj.save(**args)

    def delete(self, pk):
        team = Team.query.get_or_404(pk)
        return team.delete(), 202


class TeamResourceList(Resource):
    method_decorators = [roles_required(['ADMIN']), jwt_required]

    def get(self):
        return pagination.paginate(Team, schema, True)

    def post(self):
        parser.add_argument('members', required=True, location='json', type=list)
        args = parser.parse_args(strict=True)
        team_check = {'errors': {}}
        if Team.query.filter_by(name=args.name).first():
            team_check.get('errors').update({'name': 'Name already exist'})
        for i in args.members:
            if not User.query.filter_by(role='TEAM_MEMBER', id=i).first():
                team_check.get('errors').update({'members': 'Cant find some users with role TEAM_MEMBER'}), 400
        if team_check.get('errors'):
            return team_check, 400
        team = Team()
        for i in args.members:
            team.members.append(TeamMember(user_id=i))
        request.json.pop('members')
        obj = schema.load(data=request.json, unknown='exclude', instance=team, session=db.session)
        return obj.save(**args)


ns_team.add_resource(TeamResource, '/<int:pk>', endpoint='team')
ns_team.add_resource(TeamResourceList, '/', endpoint='teams')
