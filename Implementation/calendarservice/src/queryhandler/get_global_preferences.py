from flask import jsonify

from src.queryhandler import query
from src.queryrepository.query import get_user_global_preferences
from src.responses import ok, not_found


@query.route('/users/<int:user_id>/preferences', methods=['GET'])
def handle_get_global_preferences(user_id):

    """
    This query endpoint returns the global preferences of a user.
    :return: a json object with the global preferences on a 200 response status code.
    """
    global_preferences = get_user_global_preferences(user_id)

    if global_preferences:

        response = dict(
            global_preferences.preferences
        )

        return ok(jsonify(response))

    return not_found(jsonify(dict(error='User not found')))