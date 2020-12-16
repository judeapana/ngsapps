from flask import request
from flask_restplus import Resource, fields, inputs, Namespace
from flask_restplus.reqparse import RequestParser

from backend.ext import pagination, db
from backend.common.schema import NotificationSchema
from backend.models import Notification
from backend.resources.users import user_schema

ns_notify = Namespace('notification','Notifications for application users')

schema = NotificationSchema()
notification_schema = ns_notify.model('Notification', {
    'id': fields.Integer(),
    'user': fields.Nested(user_schema),
    'title': fields.String(),
    'message': fields.String(),
    'status': fields.Boolean(),
    'priority': fields.String(),
    'schedule_at': fields.DateTime()
})

parser = RequestParser(trim=True, bundle_errors=True)
parser.add_argument('user_id', required=True, location='json', type=int)
parser.add_argument('title', required=True, location='json', type=str)
parser.add_argument('message', required=True, location='json', type=str)
parser.add_argument('status', required=True, location='json', type=inputs.boolean)
parser.add_argument('priority', required=True, location='json', type=str)
parser.add_argument('schedule_at', required=False, location='json', type=inputs.datetime_from_iso8601)


class NotificationResource(Resource):
    @ns_notify.marshal_with(notification_schema)
    def get(self, pk):
        return Notification.query.get_or_404(pk)

    def put(self, pk):
        args = parser.parse_args(strict=True)
        notification = Notification.query.get_or_404(pk)
        obj = schema.load(data=request.json, session=db.session, instance=notification, unknown='exclude')
        args.update({'schedule_at': str(args.schedule_at)})
        return obj.save(**args)

    def delete(self, pk):
        notification = Notification.query.get_or_404(pk)
        return notification.delete(), 202


class NotificationResourceList(Resource):
    def get(self):
        return pagination.paginate(Notification, schema, True)

    def post(self):
        args = parser.parse_args(strict=True)
        notification = Notification(**args)
        args.update({'schedule_at': str(args.schedule_at)})
        return notification.save(**args), 201


ns_notify.add_resource(NotificationResource, '/<int:pk>', endpoint='notification')
ns_notify.add_resource(NotificationResourceList, '/', endpoint='notifications')
