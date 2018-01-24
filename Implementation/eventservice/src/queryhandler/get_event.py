from flask import jsonify

from src.queryhandler import query
from src.queryrepository.query import get_event, get_user_calendar_id
from src.responses import ok, not_found
from src.utils import strftime


@query.route('/users/<int:user_id>/calendars/<int:calendar_id>/events/<int:id>', methods=['GET'])
def handle_get_event(user_id, calendar_id, id):
    """
    This query endpoint returns an event resource.
    :return: a json object with the event info on a 200 response status code.
    """
    cal_id = get_user_calendar_id(user_id, calendar_id)

    if not cal_id:
        return not_found(jsonify(dict(error='Calendar not found')))

    event, event_recurrences = get_event(user_id, calendar_id, id)

    if not event:
        return not_found(jsonify(dict(error='Event not found')))

    response = dict(
        name=event.name,
        location=event.location,
        start_time=strftime(event.start_time),
        end_time=strftime(event.end_time),
        next_is_base=event.next_is_base,
        recurrence_rule=event.recurrence_rule.value,
        until=strftime(event.until),
        flex=event.flex,
        flex_duration=event.flex_duration,
        recurrences=[]
    )

    for recurrence in event_recurrences:
        response['recurrences'].append(
                dict(
                    recurrence_id=recurrence.id,
                    start_time=strftime(recurrence.start_time),
                    end_time=strftime(recurrence.end_time)
                )
        )

    return ok(jsonify(response))
