from flask import jsonify

from src.queryhandler import query
from src.queryrepository.query import get_user_global_preferences, get_calendar
from src.responses import ok, not_found


@query.route('/users/<int:user_id>/calendars/<int:id>', methods=['GET'])
def handle_get_calendar(user_id, id):

    """
    This query endpoint return a calendar of a given user.
    :return: a json object with the calendar info on a 200 response status code.
    """
    if not(get_user_global_preferences(user_id)):
        return not_found(jsonify(dict(error='User not found')))

    calendar = get_calendar(user_id, id)

    if calendar:

            response = dict(
                name=calendar.name,
                description=calendar.description,
                base=calendar.base,
                color=calendar.color,
                active=calendar.active,
                carbon=calendar.carbon,
                preferences=calendar.preferences
            )

            return ok(jsonify(response))

    return not_found(jsonify(dict(error='Calendar not found')))

