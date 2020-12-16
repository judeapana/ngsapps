from flask import request
from flask_jwt_extended import jwt_required, current_user
from flask_restplus import Resource, fields, inputs, Namespace
from flask_restplus.reqparse import RequestParser

from backend.ext import pagination, db
from backend.common.schema import ProjectSchema
from backend.models import Project, Team
from backend.resources.users import user_schema

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
    'priority': fields.String(),
    'status': fields.String(),
    'active': fields.Boolean(),
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


# used by admin and client
class ProjectResource(Resource):
    method_decorators = [jwt_required]

    @ns_project.marshal_with(project_schema, envelope='data')
    def get(self, pk):
        if current_user.role == 'CLIENT':
            return current_user.projects.filter_by(id=pk).first_or_404()
        return Project.query.get_or_404(pk)

    def put(self, pk):
        if current_user.role == 'CLIENT':
            proj = current_user.projects.filter_by(id=pk).first_or_404()
            parser.remove_argument('status')
            args = parser.parse_args(strict=True)
            args.update({'due_date': str(args.due_date)})
            if current_user.projects.filter(Project.name == args.name, Project.id != pk).first():
                return {'message': 'Please project name already exist'}, 400
            proj = schema.load(data=request.json, instance=proj, unknown='exclude', session=db.session)
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
        return proj.save(**args)

    def delete(self, pk):
        if current_user.role == 'CLIENT':
            proj = current_user.projects.filter_by(id=pk).first_or_404()
            return proj.delete(), 202
        proj = Project.query.get_or_404(pk)
        return proj.delete(), 202


class ProjectResourceList(Resource):
    method_decorators = [jwt_required]

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
        args.update({'start_date': str(args.start_date)})
        args.update({'due_date': str(args.due_date)})
        collection = []
        for team in args.teams:
            collection.append(Team.query.get(team))
        proj = Project(**args)
        proj.project_team = collection
        current_user.projects.append(proj)
        return current_user.save(**args), 201


ns_project.add_resource(ProjectResource, '/<int:pk>', endpoint='project')
ns_project.add_resource(ProjectResourceList, '/', endpoint='projects')
