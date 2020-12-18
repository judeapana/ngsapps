from flask import request
from flask_jwt_extended import current_user, jwt_required
from flask_restplus import Resource, fields, Namespace
from flask_restplus.reqparse import RequestParser

from backend.common.schema import TicketSchema
from backend.ext import pagination, db
from backend.models import Ticket
from backend.resources.project import project_schema
from backend.resources.ticket_comment import ticket_comment_schema
from backend.utils import roles_required

ns_ticket = Namespace('ticket', 'Support tickets for clients')
schema = TicketSchema()
ticket_schema = ns_ticket.model('Ticket', {
    'id': fields.Integer(),
    'uuid': fields.String(),
    'title': fields.String(),
    'project': fields.Nested(project_schema),
    'status': fields.String(),
    'comments': fields.Nested(ticket_comment_schema),
})
parser = RequestParser(trim=True, bundle_errors=True)
parser.add_argument('title', required=True, location='json', type=str)
parser.add_argument('project_id', required=True, location='json', type=int)
parser.add_argument('status', required=False, location='json', type=str)


class TicketResource(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER', 'CLIENT']), jwt_required]

    def get(self, pk):
        if current_user.role == 'CLIENT':
            return schema.dump(
                Ticket.query.filter(Ticket.project.has(user_id=current_user.id), Ticket.id == pk).first_or_404())
        return schema.dump(Ticket.query.get_or_404(pk))

    def put(self, pk):
        parser.parse_args(strict=True)
        ticket = Ticket.query.get_or_404(pk)
        obj = schema.load(data=request.json, session=db.session, unknown='exclude', instance=ticket)
        obj.save()
        return schema.dump(obj)

    def delete(self, pk):
        ticket = Ticket.query.get_or_404(pk)
        return ticket.delete(), 202


class TicketResourceList(Resource):
    method_decorators = [roles_required(['ADMIN', 'USER', 'CLIENT']), jwt_required]

    def get(self):
        if current_user.role == 'CLIENT':
            return pagination.paginate(Ticket.query.filter(Ticket.project.has(user_id=current_user.id)), schema, True)
        return pagination.paginate(Ticket, schema, True)

    def post(self):
        parser.parse_args(strict=True)
        ticket = Ticket()
        obj = schema.load(data=request.json, instance=ticket, session=db.session, unknown='exclude')
        obj.save()
        return schema.dump(obj), 201


ns_ticket.add_resource(TicketResource, '/<int:pk>', endpoint='ticket')
ns_ticket.add_resource(TicketResourceList, '/', endpoint='tickets')
