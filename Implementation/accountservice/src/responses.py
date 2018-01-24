"""
Here are defined some function to decorate REST endpoint.
"""


def ok(response):
    """
    Response to a successful GET, PUT, PATCH or DELETE
    """
    response.status_code = 200
    return response


def ko(response):
    """
    Response due to a server error
    """
    response.status_code = 500
    return response


def created(response):
    """
    Response to a POST that results in a resource creation
    """
    response.status_code = 201
    return response


def not_found(response):
    """
    Response when a non-existent resource requested
    """
    response.status_code = 404
    return response


def bad_request(response):
    """
    Response due to a bad request error
    """
    response.status_code = 400
    return response


def unauthorized(response):
    """
    When no or invalid authentication details are provided
    """
    response.status_code = 401
    return response
