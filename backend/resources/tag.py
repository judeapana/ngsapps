from flask import request
from flask_jwt_extended import jwt_required
from flask_restplus import Resource, fields, Namespace
from flask_restplus.reqparse import RequestParser

from backend.common.schema import TagSchema
from backend.ext import pagination, db
from backend.models import Tag, User
from backend.utils import roles_required

ns_tag = Namespace('tag', 'tags for yours')

schema = TagSchema()
parser = RequestParser(bundle_errors=True, trim=True)
parser.add_argument('name', required=True, type=str, location='json')

tag_schema = ns_tag.model('TagSchema', {
    'id': fields.Integer(),
    'name': fields.String()
})


class TagResource(Resource):
    method_decorators = [roles_required(['ADMIN']), jwt_required]

    @ns_tag.marshal_with(tag_schema, envelope='data')
    def get(self, pk):
        return Tag.query.get_or_404(pk)

    def put(self, pk):
        args = parser.parse_args(strict=True)
        if Tag.query.filter(Tag.name == args.name, Tag.id != pk).first():
            return {'message': 'Tag name already exist'}
        tag = Tag.query.get_or_404(pk)
        etag = schema.load(data=request.json, session=db.session, unknown='exclude', instance=tag)
        return etag.save(**args), 200

    def delete(self, pk):
        tag = Tag.query.get_or_404(pk)
        return tag.delete(), 202


class TagResourceList(Resource):
    method_decorators = [roles_required(['ADMIN']), jwt_required]

    def get(self):
        return pagination.paginate(Tag, schema, True)

    def post(self):
        args = parser.parse_args(strict=True)
        if Tag.query.filter(Tag.name == args.name).first():
            return {'message': 'Tag name already exist'}
        tag = Tag(**args)
        return tag.save(**args), 201


class UserTagResource(Resource):
    method_decorators = [roles_required(['ADMIN']), jwt_required]

    def put(self):
        par = RequestParser(trim=True, bundle_errors=True)
        par.add_argument('user', required=True, type=int, location='json')
        par.add_argument('tags', required=True, type=list, location='json')
        args = par.parse_args(strict=True)
        user = User.query.get(args.user)
        if not user:
            return {'message': 'user not found'}, 400
        user.tags = []
        for i in args.tags:
            tag = Tag.query.get(i)
            if not tag:
                return {'message': 'Tag not found'}, 400
            else:
                user.tags.append(tag)
        return user.save(**args), 200


ns_tag.add_resource(TagResource, '/<int:pk>', endpoint='tag')
ns_tag.add_resource(TagResourceList, '/', endpoint='tags')
ns_tag.add_resource(UserTagResource, '/user', endpoint='user_tag')
