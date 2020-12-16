from flask_mail import Message

from backend import mail
from backend.ext import rq


@rq.job
def send_mail_rq(message, emails=None, subject='Ngsapp App'):
    try:
        msg = Message()
        msg.subject = subject
        msg.html = message
        msg.recipients = emails
        mail.send(msg)
    except Exception as e:
        return e
