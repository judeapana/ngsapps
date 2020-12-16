import werkzeug
from flask import request
from flask_jwt_extended import jwt_required, current_user
from flask_restplus import fields, Resource, Namespace
from flask_restplus.reqparse import RequestParser

from backend import db, pagination
from backend.common import ProtectedDirField
from backend.common.schema import TicketCommentSchema
from backend.models import TicketComment, Ticket
from backend.resources.users import user_schema
from backend.utils import file_upload, delete_file

ns_ticket_comments = Namespace('ticket-comment', 'support tickets clients')

ticket_comment_schema = ns_ticket_comments.model('TicketComment', {
    'id': fields.Integer(),
    'ticket_id': fields.String(),
    'user': fields.Nested(user_schema, skip_none=True),
    'message': fields.String(),
    'file': ProtectedDirField(),
})
parser = RequestParser(trim=True, bundle_errors=True)
parser.add_argument('user_id', required=False, location='json', type=int)
parser.add_argument('message', required=True, location='json', type=str)
schema = TicketCommentSchema()


class TicketCommentResource(Resource):
    method_decorators = [jwt_required]

    @ns_ticket_comments.marshal_with(ticket_comment_schema)
    def get(self, uuid, pk):
        return TicketComment.query.filter(TicketComment.id == pk,
                                          TicketComment.ticket.has(uuid=uuid)).first_or_404()

    def put(self, uuid, pk):
        args = parser.parse_args(strict=True)
        comment = TicketComment.query.filter(TicketComment.id == pk,
                                             TicketComment.ticket.has(uuid=uuid)).first_or_404()
        obj = schema.load(data=request.json, session=db.session, unknown='exclude', instance=comment)
        return obj.save(**args)

    def delete(self, uuid, pk):
        comment = TicketComment.query.filter(TicketComment.ticket.has(uuid=uuid), TicketComment.id == pk,
                                             TicketComment.user_id == current_user.id).first_or_404()
        if current_user.role == 'ADMIN':
            comment = TicketComment.query.filter(TicketComment.ticket.has(uuid=uuid),
                                                 TicketComment.id == pk).first_or_404()
        return comment.delete(), 202


class TicketCommentResourceList(Resource):
    method_decorators = [jwt_required]

    def get(self, uuid):
        return pagination.paginate(TicketComment.query.filter(TicketComment.ticket.has(uuid=uuid)), schema, True)

    def post(self, uuid):
        args = parser.parse_args(strict=True)
        ticket = Ticket.query.filter_by(uuid=uuid).first_or_404()
        args.update({'user_id': current_user.id})
        ticket.comments.append(TicketComment(**args, ))
        return current_user.save(**args), 201


xparser = RequestParser(trim=True, bundle_errors=True)
xparser.add_argument('file', required=True, location='files', type=werkzeug.datastructures.FileStorage, )


class TicketCommentResourceFile(Resource):
    method_decorators = [jwt_required]

    def post(self, uuid, pk):
        comment = TicketComment.query.filter(TicketComment.ticket.has(uuid=uuid),
                                             TicketComment.id == pk,
                                             TicketComment.user_id == current_user.id).first_or_404()
        args = xparser.parse_args(strict=True)
        data = file_upload(args.file)
        if data.get('error'):
            return data, 400
        data.get('upload').save(data.get('full_path'))
        delete_file(comment.file)
        comment.file = data.get('filename')
        return comment.save(filename=comment.file, id=comment.id), 201

    def delete(self, uuid, pk):
        comment = TicketComment.query.filter(TicketComment.ticket.has(uuid=uuid),
                                             TicketComment.id == pk,
                                             TicketComment.user_id == current_user.id).first_or_404()
        return delete_file(comment.file)


ns_ticket_comments.add_resource(TicketCommentResource, '/comment/<uuid>/<pk>', endpoint='ticket_comment')
ns_ticket_comments.add_resource(TicketCommentResourceList, '/comments/<uuid>', endpoint='ticket_comments')
ns_ticket_comments.add_resource(TicketCommentResourceFile, '/comment/file/<uuid>/<int:pk>',
                                endpoint='ticket_comment_file')
