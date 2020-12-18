from backend.ext import rq
from backend.models import Kyc, Notification, User


@rq.job
def check_kyc_file():
    """
    This is a scheduler that checks if a user has uploaded a kyc or not a notify them
    scan every 1 hr
    :return:
    """
    kyc = Kyc.query.filter(Kyc.file == "").all()
    if kyc:
        message = "Please Upload your kyc files before you can start using our application."
        notify = Notification(user_id=kyc.user_id, title="Upload KYC Files", message=message, status=True,
                              priority='High')
        notify.save()


@rq.job
def rq_notify(message='Application Notification', title='Blank Notification'):
    users = User.query.filter(User.role == 'ADMIN').all()
    for user in users:
        user.notifications.append(Notification(title=title, message=message, status=True,
                                               priority='High'))
        user.save()


@rq.job
def rq_notify_team(users=None, title='', message=''):
    if users is None:
        return
    for user in users:
        user.notifications.append(Notification(title=title, message=message, status=True,
                                               priority='High'))
        user.save()
