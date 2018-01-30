import logging
import sys
from time import strftime

from flask import Blueprint, request

log = Blueprint('log', __name__)

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler(sys.stderr))
logger.setLevel(logging.INFO)


@log.after_app_request
def log_requests(response):
    """
    Logs externally every incoming requests following 12-factor apps principle of treating logging as a stream.
    This logs are viewed even if the app is wrapper around an application server like uwsgi.
    """
    ts = strftime('[%Y-%b-%d %H:%M-%S]')

    logger.info('Flask: {0} {1} {2} {3} {4} {5}'.
                format(ts, request.remote_addr, request.method, request.scheme, request.full_path, response.status))

    return response
