from backend.ext import rq
from backend.models import Kyc, Notification


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
