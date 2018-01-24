from flask import jsonify

from src.queryhandler import query
from src.queryrepository.query import get_all_calendar_events, get_user_calendar_id
from src.responses import ok, not_found
from src.utils import strftime


@query.route('/users/<int:user_id>/calendars/<int:calendar_id>/events', methods=['GET'])
def handle_get_all_calendar_events(user_id, calendar_id):
    """
    This query endpoint returns all the events of a user calendar.
    :return: a json object listing all the events in the user calendar on a 200 response status code.
    """
    cal_id = get_user_calendar_id(user_id, calendar_id)

    if not cal_id:
        return not_found(jsonify(dict(error='Calendar not found')))

    events = get_all_calendar_events(user_id, calendar_id)

    response = {}

    for event, event_recurrences in events:
        response[str(event.id)] = dict(
            name=event.name,
            location=event.location,
            start_time=strftime(event.start_time),
            end_time=strftime(event.end_time),
            next_is_base=event.next_is_base,
            recurrence_rule=event.recurrence_rule.value,
            until=strftime(event.until),
            flex=event.flex,
            flex_duration=event.flex_duration,
            recurrences=dict()
        )

        for recurrence in event_recurrences:
            response[str(event.id)]['recurrences'].update(
                {
                    str(recurrence.id): dict(
                        start_time=strftime(recurrence.start_time),
                        end_time=strftime(recurrence.end_time)
                    )
                }
            )

    return ok(jsonify(response))
