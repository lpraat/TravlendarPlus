import re

from validate_email import validate_email as is_valid_email


def is_unique_email(email, aggregate_status):
    return email not in (d['email'] for d in aggregate_status.values())


def validate_email(email):
    return is_valid_email(email)


def validate_password(password):
    return len(password) >= 8


def validate_name(name):
    return re.match('^[a-zA-Z]+$', name)


def validate_user_data(email, password, first_name, last_name):
    return validate_email(email) and validate_password(password) and \
           validate_name(first_name) and validate_name(last_name)


def validate_request_payload(d):
    return {'email', 'password', 'first_name', 'last_name'} == set(d)
