from marshmallow_sqlalchemy import fields

from backend import User, ma
from backend.models import Kyc, Team, Tag, Project, ProjectFile, ProjectComment, Task, Ticket, TicketComment, \
    Notification


class TagSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Tag
        load_instance = True


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        exclude = ['password', 'uuid']

    tags = fields.Nested(TagSchema(), many=True)


class KYCSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Kyc
        load_instance = True

    user = fields.Nested(UserSchema())


class TeamSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Team
        load_instance = True

    users = fields.Nested(UserSchema(), many=True)


class ProjectSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Project
        load_instance = True

    user = fields.Nested(UserSchema())


class ProjectFileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProjectFile
        load_instance = True


class ProjectCommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProjectComment
        load_instance = True


class TaskSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Task
        load_instance = True

    user = fields.Nested(UserSchema())
    project = fields.Nested(ProjectSchema())


class TicketSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Ticket
        load_instance = True

    comments = fields.Nested('TicketCommentSchema', many=True)


class TicketCommentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = TicketComment
        load_instance = True


class NotificationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        load_instance = True

    user = fields.Nested(UserSchema())
