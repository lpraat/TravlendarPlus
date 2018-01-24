def validate_request_paylaod(d):
    """
    Returns true if the payload of the login request contains the correct data
    """
    return {'email', 'password'} == set(d)
