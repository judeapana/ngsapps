from flask import request
from flask_jwt_extended import jwt_required, current_user
from flask_restplus import Resource, fields, inputs, Namespace, marshal
from flask_restplus.reqparse import RequestParser

from backend.common.schema import ProjectSchema
from backend.ext import pagination, db
from backend.models import Project, Team
from backend.resources.team import team_schema
from backend.resources.users import user_schema
from backend.tasks import rq_notify
from backend.utils import roles_required

ns_project = Namespace('project', 'Project management')

project_schema = ns_project.model('Project', {
    'id': fields.Integer(),
    'uuid': fields.String(),
    'user': fields.Nested(user_schema),
    'name': fields.String(),
    'description': fields.String(),
    'start_date': fields.DateTime(),
    'due_date': fields.DateTime(),
    'budget': fields.Float(),
    "teams": fields.Nested(team_schema, allow_null=True),
    'priority': fields.String(),
    'status': fields.String(),
    'active': fields.Boolean(),
    'created': fields.DateTime(),
})
schema = ProjectSchema()
parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('name', required=True, location='json', type=str)
parser.add_argument('description', required=True, location='json', type=str)
parser.add_argument('due_date', required=True, location='json', type=inputs.date_from_iso8601)
parser.add_argument('budget', required=True, location='json', type=float)
parser.add_argument('priority', required=True, location='json', type=str)
parser.add_argument('active', required=True, location='json', type=inputs.boolean)
parser.add_argument('status', required=False, location='json', type=str)


class ProjectResource(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER', 'CLIENT']), jwt_required]

    def get(self, pk):
        if current_user.role == 'CLIENT':
            return marshal(current_user.projects.filter_by(id=pk).first_or_404(), project_schema)
        return schema.dump(Project.query.get_or_404(pk))

    def put(self, pk):
        if current_user.role == 'CLIENT':
            proj = current_user.projects.filter_by(id=pk).first_or_404()
            parser.remove_argument('status')
            args = parser.parse_args(strict=True)
            args.update({'due_date': str(args.due_date)})
            if current_user.projects.filter(Project.name == args.name, Project.id != pk).first():
                return {'message': 'Please project name already exist'}, 400
            proj = schema.load(data=request.json, instance=proj, unknown='exclude', session=db.session)
            rq_notify.queue(
                message=f'Project <a href="{request.url}">Project by {current_user.full_name}</a> has been updated',
                title='Project has been updated')
            return proj.save(**args)

        parser.add_argument('start_date', required=True, location='json', type=inputs.date_from_iso8601)
        parser.add_argument('teams', required=True, type=list, location='json')
        args = parser.parse_args(strict=True)
        args.update({'start_date': str(args.start_date)})
        args.update({'due_date': str(args.due_date)})
        proj = Project.query.get_or_404(pk)
        if Project.query.filter(Project.name == args.name, Project.id != pk).first():
            return {'message': 'Please project name already exist'}, 400
        proj.project_team = []
        collection = []
        for team in args.teams:
            collection.append(Team.query.get(team))
        proj = schema.load(data=request.json, instance=proj, unknown='exclude', session=db.session)
        proj.project_team = collection
        proj.save()
        return schema.dump(proj)

    def delete(self, pk):
        if current_user.role == 'CLIENT':
            proj = current_user.projects.filter_by(id=pk).first_or_404()
            return proj.delete(), 202
        proj = Project.query.get_or_404(pk)
        return proj.delete(), 202


class ProjectResourceList(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER', 'CLIENT']), jwt_required]

    def get(self):
        if current_user.role == 'CLIENT':
            return pagination.paginate(current_user.projects, schema, True)
        return pagination.paginate(current_user.projects, schema, True)

    def post(self):
        if current_user.role == 'CLIENT':
            parser.remove_argument('status')
            args = parser.parse_args(strict=True)
            if current_user.projects.filter_by(name=args.name).first():
                return {'message': 'Please project name already exist'}, 400
            current_user.projects.append(Project(**args))
            args.update({'due_date': str(args.due_date)})
            return current_user.save(**args), 201
        parser.add_argument('start_date', required=True, location='json', type=inputs.date_from_iso8601)
        parser.add_argument('teams', required=True, type=list, location='json')
        args = parser.parse_args(strict=True)
        # args.update({'start_date': str(args.start_date)})
        # args.update({'due_date': str(args.due_date)})
        collection = []
        for team in args.teams:
            collection.append(Team.query.get(team))
        args.pop('teams')
        proj = Project(**args)
        proj.project_team = collection
        current_user.projects.append(proj)
        current_user.save(**args)
        return schema.dump(proj), 201


ns_project.add_resource(ProjectResource, '/<int:pk>', endpoint='project')
ns_project.add_resource(ProjectResourceList, '/', endpoint='projects')
