from flask import jsonify

from src.queryhandler import query
from src.queryrepository.query import get_all_user_calendars, get_user_global_preferences
from src.responses import ok, not_found


@query.route('/users/<int:user_id>/calendars', methods=['GET'])
def handle_get_all_calendars(user_id):

    """
    This query endpoint returns all the calendars of a given user.
    :return: a json object with a list of all the calendars on a 200 response status code.
    """
    if not(get_user_global_preferences(user_id)):
        return not_found(jsonify(dict(error='User not found')))

    calendars = get_all_user_calendars(user_id)
    response = dict(calendars=[])

    for calendar in calendars:
        response['calendars'].append(dict(
            id=calendar.id,
            name=calendar.name,
            description=calendar.description,
            base=calendar.base,
            color=calendar.color,
            active=calendar.active,
            carbon=calendar.carbon,
            preferences=calendar.preferences
        ))

    return ok(jsonify(response))