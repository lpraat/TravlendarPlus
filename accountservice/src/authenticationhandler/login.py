import logging

import jwt
import requests
from flask import request, jsonify

from src.authenticationhandler import auth
from src.authenticationhandler.validate_data import validate_request_paylaod
from src.queryrepository.query import get_user_id_by_credentials
from src.responses import ko, ok, bad_request

logger = logging.getLogger(__name__)

KONG_IP = "172.18.0.2"  # todo configure this ip


@auth.route('/login', methods=['POST'])
def handle_login():
    """
    Login endpoint. It is used for logging a user in.
    If the email and the password passed in the request body are valid ones it returns a
    valid token for the authentication in the API gateway.

    """
    data = request.get_json()

    if validate_request_paylaod(data):
        email = data['email']
        password = data['password']
        user_id = get_user_id_by_credentials(email, password)

        if user_id:
            # retrieves a new token for this user
            KONG_JWT_API = f"http://{KONG_IP}:8001/consumers/{email}/jwt"
            response = requests.post(KONG_JWT_API, data={"algorithm": "HS256"})
            data = response.json()
            headers = {
                "typ": "JWT",
                "alg": "HS256"
            }
            claims = {
                "iss": data['key']
            }
            token = jwt.encode(
                claims,
                data['secret'],
                headers=headers
            )

            if not response.status_code == 201:
                logger.error(f'Could not build token for {request}')
                return ko(dict(error='Could not build token'))

            logger.info(f"Generated JWT Token: {token} for user {user_id}")
            return ok(jsonify(dict(
                auth_token=token.decode(),
                id=user_id
            )))

    return bad_request(jsonify(dict(error='invalid_data')))
