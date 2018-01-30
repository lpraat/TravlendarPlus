from flask import jsonify

from src.queryhandler import query
from src.queryrepository.query import get_schedule
from src.responses import ok
from src.utils import strftime


@query.route('/users/<int:user_id>/schedule', methods=['GET'])
def handle_get_schedule(user_id):

    """
    This query endpoint returns the user schedule.
    :return: a json object with the list of all the recurrences in the user schedule on a 200 response status code.
    """
    recurrences_and_names = get_schedule(user_id)

    response = dict(recurrences=[])
    for recurrence, name in recurrences_and_names:
        response['recurrences'].append(
            dict(
                user_id=user_id,
                calendar_id=recurrence.calendar_id,
                event_id=recurrence.event_id,
                id=recurrence.id,
                start_time=strftime(recurrence.start_time),
                end_time=strftime(recurrence.end_time),
                event_name=name
            )
        )
    return ok(jsonify(response))

