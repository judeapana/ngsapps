from backend.ext import rq


@rq.job()
# email, message, subject=''
def send_mail_rq():
    pass

    # try:
    # msg = Message()
    # msg.recipients = [email]
    # msg.subject = subject
    # msg.body = message
    # mail.send(msg)
    # except Exception as e:
    #     return e


@rq.job
def rq_login_notify(email):
    pass
    # send_mail_rq(email, LOGIN_NOTIFY.format())
