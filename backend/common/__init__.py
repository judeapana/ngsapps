import phonenumbers
from flask import url_for
from flask_restplus.fields import Raw


def string(value, name):
    """
    Validate if String is greater than 3 characters
    :param value:
    :param name:
    :return:
    """
    if not value:
        raise ValueError(f'{name.replace("_", " ")} is required')
    if len(value) < 3:
        raise ValueError(f'{name.replace("_", " ")} must be at least 3 characters long')
    return value


def phone_number(value, name):
    """
    Validate phone number using python - phonenumbers
    :param value:
    :param name:
    :return:
    """
    if not value:
        raise ValueError(f'{name.replace("_", " ")} is required')
    try:
        number = phonenumbers.parse(value, "GH")
        if not phonenumbers.is_valid_number(number):
            raise ValueError(f'{name.replace("_", " ")} is invalid')
    except Exception as e:
        raise ValueError(f'{name.replace("_", " ")} is invalid')
    return value


class ProtectedDirField(Raw):
    """
        Format url to /protected path
    """

    def format(self, value):
        if not value:
            return ''
        return url_for('api.protected_dir', filename=value, _external=True)
