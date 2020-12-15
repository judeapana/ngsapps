from marshmallow_sqlalchemy import fields

from backend import User, ma
from backend.models import Kyc, Team, Tag


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
