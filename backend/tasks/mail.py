from flask_mail import Message

from backend import rq, mail


@rq.job
def send_mail_rq(email, message, subject=''):
    try:
        msg = Message(subject=subject, recipients=[email])
        msg.html = message
        mail.send(msg)
    except Exception as e:
        return e
