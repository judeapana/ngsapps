import werkzeug
from flask_jwt_extended import current_user, jwt_required
from flask_restplus import Resource, fields, Namespace
from flask_restplus.reqparse import RequestParser

from backend.common import ProtectedDirField
from backend.common.schema import ProjectFileSchema
from backend.ext import pagination
from backend.models import Project, ProjectFile
from backend.resources.project import project_schema
from backend.utils import delete_file, file_upload, roles_required

ns_proj_files = Namespace('project-files', 'Project files upload')
schema = ProjectFileSchema()

project_files_schema = ns_proj_files.model('ProjectFiles', {
    'id': fields.Integer(),
    'project': fields.Nested(project_schema),
    'attached_file': ProtectedDirField(),
    'description': fields.String()
})


class ProjectFileResource(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER', 'CLIENT']), jwt_required]

    @ns_proj_files.marshal_with(project_files_schema, envelope='data')
    def get(self, uuid, pk):
        if current_user.role == 'CLIENT':
            project = current_user.projects.filter_by(uuid=uuid).first_or_404()
            return project.files.filter_by(id=pk).first_or_404()
        proj = Project.query.filter_by(uuid=uuid).first_or_404()
        return proj.files.filter_by(id=pk).first_or_404()

    def delete(self, uuid, pk):
        if current_user.role == 'CLIENT':
            project = current_user.projects.filter_by(uuid=uuid).first_or_404()
            file = project.files.filter_by(id=pk).first_or_404()
            delete_file(file.attached_file)
            return file.delete(), 202
        proj = Project.query.filter_by(uuid=uuid).first_or_404()
        file = proj.files.filter_by(id=pk).first_or_404()
        data = delete_file(file.attached_file)
        if data.get('message'):
            return data, 400
        return data, 202


xparser = RequestParser(bundle_errors=True, trim=True)
xparser.add_argument('files', required=True, location='files', type=werkzeug.datastructures.FileStorage,
                     action='append')
xparser.add_argument('description', required=True, location='form', type=str)


class ProjectFileResourceList(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER', 'CLIENT']), jwt_required]

    def get(self, uuid):
        project_files_schema.pop('project')
        if current_user.role == 'CLIENT':
            fil = current_user.projects.filter_by(uuid=uuid).first_or_404()
            return pagination.paginate(fil.files, schema, True)

        return pagination.paginate(ProjectFile.query.filter(ProjectFile.project.has(uuid=uuid)), schema, True)

    def post(self, uuid):
        args = xparser.parse_args(strict=True)
        if current_user.role == 'CLIENT':
            project = current_user.projects.filter_by(uuid=uuid).first_or_404()
        else:
            project = Project.query.filter_by(uuid=uuid).first_or_404()
        for file in args.files:
            data = file_upload(file)
            if data.get('error'):
                return data, 400
        for file in args.files:
            data = file_upload(file, )
            data.get('upload').save(data.get('full_path'))
            project.files.append(ProjectFile(attached_file=data.get('filename'), description=args.description))
        return project.save(), 202


ns_proj_files.add_resource(ProjectFileResource, '/<uuid>/<int:pk>', endpoint='project_file')
ns_proj_files.add_resource(ProjectFileResourceList, '/<uuid>', endpoint='projects_files')
