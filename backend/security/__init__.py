from flask_restplus import Namespace

auth = Namespace('auth', description='Application authentication', )
from . import login, confirm_account, forgot_password, register, reset_password, resend_account_activation, logout
