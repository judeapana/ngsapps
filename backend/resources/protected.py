import os

from flask import send_from_directory, current_app
from flask_jwt import jwt_required
from flask_restful import Resource
from flask_restplus import Namespace

protected = Namespace('protected', 'Protected route for logged in users')


class ProtectedDirResource(Resource):
    method_decorators = [jwt_required]

    def get(self, filename):
        return send_from_directory(os.path.join(current_app.root_path, 'static', 'protected'), filename=filename)


protected.add_resource(ProtectedDirResource, '/files/<filename>', endpoint='protected_dir')
