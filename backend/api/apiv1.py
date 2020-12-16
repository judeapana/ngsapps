from flask import Blueprint
from flask_restplus import Api

from backend.resources.kyc import ns_kyc
from backend.resources.notification import ns_notify
from backend.resources.project import ns_project
from backend.resources.project_comment import ns_proj_comment
from backend.resources.project_files import ns_proj_files
from backend.resources.protected import protected
from backend.resources.tag import ns_tag
from backend.resources.task import ns_task
from backend.resources.team import ns_team
from backend.resources.ticket import ns_ticket
from backend.resources.ticket_comment import ns_ticket_comments
from backend.resources.users import ns_user
from backend.security import auth

bapi = Blueprint('api', __name__, url_prefix='/api')
api = Api(bapi, title='Ngsapp', catch_all_404s=True, serve_challenge_on_401=True)

api.add_namespace(auth)
api.add_namespace(ns_kyc)
api.add_namespace(ns_notify)
api.add_namespace(ns_project)
api.add_namespace(ns_proj_comment)
api.add_namespace(ns_proj_files)
api.add_namespace(ns_user)
api.add_namespace(protected)
api.add_namespace(ns_tag)
api.add_namespace(ns_task)
api.add_namespace(ns_ticket)
api.add_namespace(ns_ticket_comments)
api.add_namespace(ns_team)
