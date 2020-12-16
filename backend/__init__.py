from uuid import UUID

import wtforms_json
from flask import Flask

from backend.config import DevelopmentConfig
from backend.ext import cors, db, pagination, bcrypt, migrate, rq, ma, mail, jwt
from backend.models import User
from backend.resources import api, bapi
from backend.resources.kyc import KYCResourceList, KYCResource, ClientKYCResource, KycUploadResource
from backend.resources.notification import NotificationResourceList, NotificationResource
from backend.resources.project import ProjectResource, ProjectResourceList
from backend.resources.project_comment import ProjectCommentResourceList, ProjectCommentResource, \
    ProjectCommentResourceFile
from backend.resources.project_files import ProjectFileResourceList, ProjectFileResource
from backend.resources.tag import TagResource, TagResourceList, UserTagResource
from backend.resources.task import TaskResourceList, TaskResource
from backend.resources.team import TeamResource, TeamResourceList
from backend.resources.ticket import TicketResource, TicketResourceList
from backend.resources.ticket_comment import TicketCommentResource, TicketCommentResourceList, TicketCommentResourceFile
from backend.resources.users import UserResource, UserResourceList
from backend.security.confirm_account import ConfirmAccountResource
from backend.security.forgot_password import ForgotPasswordResource
from backend.security.login import LoginResource
from backend.security.protected import ProtectedDirResource
from backend.security.register import RegisterResource
from backend.security.resend_account_activation import ResendAccountActivationResource
from backend.security.reset_password import ResetPasswordResource


def create_app():
    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    pagination.init_app(app, db)
    bcrypt.init_app(app)
    migrate.init_app(app, db)
    rq.init_app(app)
    ma.init_app(app)
    mail.init_app(app)
    wtforms_json.init()
    app.register_blueprint(bapi)
    api.add_resource(UserResourceList, '/users', endpoint='users')
    api.add_resource(UserResource, '/user/<int:pk>', endpoint='user')
    api.add_resource(LoginResource, '/login', endpoint='login')
    api.add_resource(ForgotPasswordResource, '/forgot', endpoint='forgot')
    api.add_resource(ConfirmAccountResource, '/confirm', endpoint='confirm')
    api.add_resource(RegisterResource, '/register', endpoint='register')
    api.add_resource(ResendAccountActivationResource, '/re-confirm', endpoint='re_confirm')
    api.add_resource(ResetPasswordResource, '/reset-pwd', endpoint='reset_pwd')

    api.add_resource(KYCResourceList, 'kycs', endpoint='kycs')
    api.add_resource(KYCResource, 'kyc/<int:pk>', endpoint='kyc')
    api.add_resource(ClientKYCResource, '/client/kyc', endpoint='client_kyc')
    api.add_resource(KycUploadResource, '/client/kyc/file', endpoint='client_kyc_file')

    api.add_resource(TeamResource, '/team/<int:pk>', endpoint='team')
    api.add_resource(TeamResourceList, '/teams', endpoint='teams')

    api.add_resource(TagResource, '/tag/<int:pk>', endpoint='tag')
    api.add_resource(TagResourceList, '/tags', endpoint='tags')

    api.add_resource(UserTagResource, '/user/tag', endpoint='user_tag')

    api.add_resource(ProjectResource, '/project/<int:pk>', endpoint='project')
    api.add_resource(ProjectResourceList, '/projects', endpoint='projects')

    api.add_resource(ProjectFileResource, '/project/<uuid>/<int:pk>', endpoint='project_file')
    api.add_resource(ProjectFileResourceList, '/project/<uuid>', endpoint='projects_files')

    api.add_resource(ProjectCommentResource, '/project/comment/<uuid>/<int:pk>', endpoint='projects_comment')
    api.add_resource(ProjectCommentResourceFile, '/project/comment/file/<uuid>/<int:pk>',
                     endpoint='projects_comment_file')
    api.add_resource(ProjectCommentResourceList, '/project/comments/<uuid>', endpoint='projects_comments')

    api.add_resource(TaskResource, '/task/<int:pk>', endpoint='task')
    api.add_resource(TaskResourceList, '/tasks', endpoint='tasks')

    api.add_resource(NotificationResource, '/notification/<int:pk>', endpoint='notification')
    api.add_resource(NotificationResourceList, '/notifications', endpoint='notifications')

    api.add_resource(TicketResource, '/ticket/<int:pk>', endpoint='ticket')
    api.add_resource(TicketResourceList, '/tickets', endpoint='tickets')

    api.add_resource(TicketCommentResource, '/ticket/comment/<uuid>/<pk>', endpoint='ticket_comment')
    api.add_resource(TicketCommentResourceList, '/ticket/comments/<uuid>', endpoint='ticket_comments')
    api.add_resource(TicketCommentResourceFile, '/ticket/comment/file/<uuid>/<int:pk>', endpoint='ticket_comment_file')

    api.add_resource(ProtectedDirResource, '/files/<filename>', endpoint='protected_dir')

    @jwt.user_loader_callback_loader
    def load_user(identity):
        return User.query.filter(User.uuid == UUID(identity)).one()

    return app
