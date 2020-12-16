import werkzeug
from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restplus import Resource, fields, inputs, Namespace
from flask_restplus.reqparse import RequestParser

from backend.ext import pagination, db
from backend.common import ProtectedDirField
from backend.common.schema import ProjectCommentSchema
from backend.models import ProjectComment, Project
from backend.resources.project import project_schema
from backend.resources.users import user_schema
from backend.utils import file_upload, delete_file

ns_proj_comment = Namespace('project-comments', 'Project comments by users')
project_comment_schema = ns_proj_comment.model('Comments', {
    'id': fields.Integer(),
    'user': fields.Nested(user_schema),
    'project': fields.Nested(project_schema),
    'message': fields.String(),
    'hide': fields.Boolean(),
    'file': ProtectedDirField(),
})

schema = ProjectCommentSchema()
parser = RequestParser(trim=True, bundle_errors=True)
parser.add_argument('message', required=True, type=str, location='json')


# for admin, team member,users
class ProjectCommentResource(Resource):
    method_decorators = [jwt_required]

    @ns_proj_comment.marshal_with(project_comment_schema)
    def get(self, uuid, pk):
        return ProjectComment.query.filter(ProjectComment.id == pk,
                                           ProjectComment.project.has(uuid=uuid)).first_or_404()

    def put(self, uuid, pk):
        args = parser.parse_args(strict=True)
        parser.add_argument('hide', required=False, type=inputs.boolean, location='json')
        comment = ProjectComment.query.filter(ProjectComment.id == pk,
                                              ProjectComment.project.has(uuid=uuid)).first_or_404()
        obj = schema.load(data=request.json, session=db.session, unknown='exclude', instance=comment)
        return obj.save(**args)

    def delete(self, uuid, pk):
        comment = current_user.project_comments.filter(ProjectComment.id == pk,
                                                       ProjectComment.project.has(uuid=uuid)).first_or_404()
        return comment.delete(), 202


class ProjectCommentResourceList(Resource):
    method_decorators = [jwt_required]

    def get(self, uuid):
        return pagination.paginate(ProjectComment.query.filter(ProjectComment.project.has(uuid=uuid)), schema, True)

    def post(self, uuid):
        args = parser.parse_args(strict=True)
        project = Project.query.filter_by(uuid=uuid).first_or_404()
        project.comments.append(ProjectComment(**args, user_id=current_user.id))
        return current_user.save(**args), 201


xparser = RequestParser(trim=True, bundle_errors=True)
xparser.add_argument('file', required=True, location='files', type=werkzeug.datastructures.FileStorage, )


class ProjectCommentResourceFile(Resource):
    method_decorators = [jwt_required]

    def post(self, uuid, pk):
        comment = current_user.project_comments.filter(ProjectComment.id == pk,
                                                       ProjectComment.project.has(uuid=uuid)).first_or_404()
        args = xparser.parse_args(strict=True)
        data = file_upload(args.file)
        if data.get('error'):
            return data, 400
        data.get('upload').save(data.get('full_path'))
        delete_file(comment.file)
        comment.file = data.get('filename')
        return comment.save(filename=comment.file, id=comment.id), 201

    def delete(self, uuid, pk):
        comment = current_user.project_comments.filter(ProjectComment.id == pk,
                                                       ProjectComment.project.has(uuid=uuid)).first_or_404()
        return delete_file(comment.file)


ns_proj_comment.add_resource(ProjectCommentResource, '/comment/<uuid>/<int:pk>', endpoint='projects_comment')
ns_proj_comment.add_resource(ProjectCommentResourceFile, '/comment/file/<uuid>/<int:pk>',
                             endpoint='projects_comment_file')
ns_proj_comment.add_resource(ProjectCommentResourceList, '/comments/<uuid>', endpoint='projects_comments')
