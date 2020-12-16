from flask import request
from flask_restplus import Resource, fields, Namespace
from flask_restplus.reqparse import RequestParser

from backend.ext import pagination, db
from backend.common.schema import TicketSchema
from backend.models import Ticket
from backend.resources.project import project_schema
from backend.resources.ticket_comment import ticket_comment_schema

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
    def get(self, pk):
        return Ticket.query.get_or_404(pk)

    def put(self, pk):
        args = parser.parse_args(strict=True)
        ticket = Ticket.query.get_or_404(pk)
        obj = schema.load(data=request.json, session=db.session, unknown='exclude', instance=ticket)
        return obj.save(**args)

    def delete(self, pk):
        ticket = Ticket.query.get_or_404(pk)
        return ticket.delete(), 202


class TicketResourceList(Resource):
    def get(self):
        return pagination.paginate(Ticket, schema, True)

    def post(self):
        args = parser.parse_args(strict=True)
        ticket = Ticket(**args)
        return ticket.save(**args), 201


ns_ticket.add_resource(TicketResource, '/<int:pk>', endpoint='ticket')
ns_ticket.add_resource(TicketResourceList, '/', endpoint='tickets')
