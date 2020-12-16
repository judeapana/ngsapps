from flask import request
from flask_jwt_extended import jwt_required, current_user
from flask_restplus import Resource, fields, inputs, Namespace
from flask_restplus.reqparse import RequestParser

from backend import pagination, db
from backend.common.schema import TaskSchema
from backend.models import Task
from backend.resources.project import project_schema
from backend.resources.users import user_schema

ns_task = Namespace('task', 'Task for projects')

schema = TaskSchema()
task_schema = ns_task.model('Task', {
    'id': fields.Integer(),
    'name': fields.String(),
    'user': fields.Nested(user_schema),
    'project': fields.Nested(project_schema),
    'description': fields.String(),
    'date': fields.DateTime(),
    'due_date': fields.DateTime(),
    'status': fields.String(),
})
parser = RequestParser(trim=True, bundle_errors=True)
parser.add_argument('name', required=True, location='json', type=str)
parser.add_argument('project_id', required=True, location='json', type=int)
parser.add_argument('description', required=True, location='json', type=str)
parser.add_argument('date', required=True, location='json', type=inputs.datetime_from_iso8601)
parser.add_argument('due_date', required=True, location='json', type=inputs.datetime_from_iso8601)
parser.add_argument('status', required=False, location='json', type=inputs.boolean)


class TaskResource(Resource):
    method_decorators = [jwt_required]

    @ns_task.marshal_with(task_schema)
    def get(self, pk):
        return Task.query.get_or_404(pk)

    def put(self, pk):
        args = parser.parse_args(strict=True)
        task = Task.query.get_or_404(pk)
        obj = schema.load(data=request.json, instance=task, session=db.session, unknown='exclude')
        args.update({'date': str(args.date)})
        args.update({'due_date': str(args.due_date)})
        return obj.save(**args), 201

    def delete(self, pk):
        task = Task.query.get_or_404(pk)
        return task.delete(), 202


class TaskResourceList(Resource):
    method_decorators = [jwt_required]

    def get(self):
        return pagination.paginate(Task, task_schema)

    def post(self):
        args = parser.parse_args(strict=True)
        task = Task(**args, user=current_user)
        args.update({'date': str(args.date)})
        args.update({'due_date': str(args.due_date)})
        print(args.date)
        print(args.due_date)
        return task.save(**args), 201


ns_task.add_resource(TaskResource, '/<int:pk>', endpoint='task')
ns_task.add_resource(TaskResourceList, '/', endpoint='tasks')
