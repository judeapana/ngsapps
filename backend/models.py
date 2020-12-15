import secrets
from uuid import uuid4

from flask import current_app
from itsdangerous import TimedJSONWebSignatureSerializer, BadSignature
from sqlalchemy_utils import Timestamp, EmailType, UUIDType, PhoneNumberType

from backend.common.active_record import ActiveRecord
from backend.ext import db, bcrypt


class User(db.Model, ActiveRecord, Timestamp):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    uuid = db.Column(UUIDType, default=uuid4(), nullable=False)
    img = db.Column(db.String(100), default='default.png')
    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(EmailType, nullable=False, unique=True, info={'label': 'Email Address'})
    status = db.Column(db.Boolean, default=True)
    gender = db.Column(db.Enum('Male', 'Female', 'Others'))
    confirmed = db.Column(db.Boolean, default=False)
    last_logged_in = db.Column(db.DateTime)
    role = db.Column(db.Enum('ADMIN', 'TEAM_MEMBER', 'CLIENT', 'USER'), nullable=False)
    kyc_doc = db.relationship('Kyc', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                              lazy=True, uselist=False)
    teams = db.relationship('Team', backref=db.backref('users'), secondary='team_member', lazy='dynamic',
                            cascade='all,delete')
    tags = db.relationship('Tag', backref=db.backref('users'), secondary='user_tag', lazy='dynamic',
                           cascade='all,delete')
    notifications = db.relationship('Notification', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                                    lazy='dynamic')
    jobs = db.relationship('RqJob', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                           lazy='dynamic')
    project_comments = db.relationship('ProjectComment', backref=db.backref('user'),
                                       cascade='all,delete,delete-orphan',
                                       lazy='dynamic')
    projects = db.relationship('Project', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                               lazy='dynamic')
    billing = db.relationship('BillingInfo', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                              uselist=True, lazy=True)
    tasks = db.relationship('Task', backref=db.backref('user'), cascade='all,delete,delete-orphan',
                            lazy='dynamic')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    def create_token(self, expires=172800):
        jst = TimedJSONWebSignatureSerializer(secret_key=current_app.secret_key, expires_in=expires)
        return jst.dumps({'id': str(self.uuid)}).decode()

    @staticmethod
    def authenticate_token(token):
        try:
            jst = TimedJSONWebSignatureSerializer(secret_key=current_app.secret_key)
            return jst.loads(token)
        except BadSignature:
            return None

    @staticmethod
    def user_exist(data):
        response = {'errors': {}}
        if User.query.filter_by(username=data.get('username')).first():
            response.get('errors').update({'username': 'username already exist'})
        if User.query.filter_by(email=data.get('email')).first():
            response.get('errors').update({'email_address': 'email address already exist'})
        return response if response.get('errors') else None


class BillingInfo(db.Model, ActiveRecord, Timestamp):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)


class Kyc(db.Model, ActiveRecord, Timestamp):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    business_name = db.Column(db.String(100), nullable=False, unique=True)
    ident = db.Column(db.String(100), nullable=False, unique=True)
    about_business = db.Column(db.Text, nullable=False, unique=True)
    phone_number = db.Column(PhoneNumberType(region='GH'), nullable=False, unique=True)
    country = db.Column(db.String(100), nullable=False)
    file = db.Column(db.String(100), nullable=True)
    status = db.Column(db.Enum('Approved', 'Pending', 'Disapproved', 'Suspended', 'Processing'), nullable=False,
                       default='Pending')


class Team(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    email_address = db.Column(EmailType)
    description = db.Column(db.Text)
    members = db.relationship('TeamMember', backref=db.backref('team'), cascade='all,delete,delete-orphan',
                              lazy='dynamic')


class TeamMember(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='cascade'), nullable=False)


class UserTag(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id', ondelete='cascade'), nullable=False)


class Tag(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    # users = db.relationship('UserTag', backref=db.backref('tag'), cascade='all,delete,delete-orphan',
    #                           lazy='dynamic')


class Project(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Numeric(10, 2, asdecimal=False), nullable=False)
    priority = db.Column(db.Enum('High', 'Low', 'Normal'), nullable=False, default='Low')
    files = db.relationship('ProjectFile', backref=db.backref('project'), lazy='dynamic',
                            cascade='all,delete,delete-orphan')
    tickets = db.relationship('Ticket', backref=db.backref('project'), cascade='all,delete,delete-orphan',
                              lazy='dynamic')
    project_team = db.relationship('Team', backref=db.backref('project'), cascade='all,delete',
                                   secondary='project_team')
    # member_team = db.relationship('User', backref=db.backref('project'), cascade='all,delete',
    #                               secondary='member_project')
    tasks = db.relationship('Task', backref=db.backref('project'), cascade='all,delete,delete-orphan',
                            lazy='dynamic')
    comments = db.relationship('ProjectComment', backref=db.backref('project'), cascade='all,delete,delete-orphan',
                               lazy='dynamic')
    status = db.Column(db.Enum('Reviewing', 'Approved', 'Disapproved', 'Complete', 'Incomplete', 'Halt'),
                       default='Reviewing')
    active = db.Column(db.Boolean, nullable=False, default=True)


class ProjectFile(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='cascade'), nullable=False)
    attached_file = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)


class ProjectComment(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='cascade'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    file = db.Column(db.String(200))


# class MemberProject(db.Model, ActiveRecord):
#     id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
#     project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='cascade'), nullable=False)


class ProjectTeam(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='cascade'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='cascade'), nullable=False)


class Ticket(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    uuid = db.Column(db.String(100), default=secrets.token_hex(10), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='cascade'), nullable=False)
    status = db.Column(db.Enum('Achieve', 'Open', 'Closed'))
    comments = db.relationship('TicketComment', backref=db.backref('ticket'), cascade='all,delete,delete-orphan',
                               lazy='dynamic')


class TicketComment(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id', ondelete='cascade'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    file = db.Column(db.String(200))

    # files = db.relationship('TicketFile', backref=db.backref('ticket_comment'), cascade='all,delete,delete-orphan',
    #                         lazy='dynamic')


# class TicketFile(db.Model, ActiveRecord):
#     id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
#     ticket_comment_id = db.Column(db.Integer, db.ForeignKey('ticket_comment.id', ondelete='cascade'), nullable=False)
#     attached_file = db.Column(db.String(200), nullable=False)
#     description = db.Column(db.Text)


class Task(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id', ondelete='cascade'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Ongoing', 'Complete', 'Upcoming'), nullable=False)
    # team_members = db.relationship('Team', backref=db.backref('task'), secondary='task_team_member',
    #                                cascade='all,delete',
    #                                lazy='dynamic')


# class TaskTeamMember(db.Model, ActiveRecord):
#     id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
#     team_id = db.Column(db.Integer, db.ForeignKey('team.id', ondelete='cascade'), nullable=False)
#     task_id = db.Column(db.Integer, db.ForeignKey('task.id', ondelete='cascade'), nullable=False)


class Notification(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Boolean, default=False, nullable=False)
    priority = db.Column(db.Enum('High', 'Low', 'Normal'))
    schedule_at = db.Column(db.Date)


class RqJob(db.Model, ActiveRecord):
    id = db.Column(db.Integer, primary_key=True, nullable=False, unique=True)
    uuid = db.Column(UUIDType, nullable=False, default=uuid4())
    description = db.Column(db.String(100), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='cascade'), nullable=False)
