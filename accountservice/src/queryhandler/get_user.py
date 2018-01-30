from flask import jsonify

from src.queryhandler import query
from src.queryrepository.query import get_user_by_id
from src.responses import ok, not_found


@query.route('/users/<int:user_id>', methods=['GET'])
def handle_get(user_id):
    """
    This is the only endpoint query side. It is used for retrieving a user resource data.
    :return: a json object with the user info on a 200 response status code.
    """
    user = get_user_by_id(user_id)

    if user:
        return ok(jsonify(dict(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name
        )))

    return not_found(jsonify(dict(error='User not found')))
