from flask import json
from sqlalchemy.exc import SQLAlchemyError

from src.constants import PREFERENCES_CREATED_EVENT, PREFERENCES_MODIFIED_EVENT, PREFERENCES_DELETED_EVENT, \
    CALENDAR_CREATED_EVENT, CALENDAR_MODIFIED_EVENT, CALENDAR_DELETED_EVENT
from src.eventrepository.data.event import CalendarEvent
from src.utils import make_calendar_preferences_consistent


def build_calendar_aggregate():
    """
    This builds the calendar aggregate by chronologically applying events in the event store.
    :return: the aggregate status.
    """
    aggregate_status = {}
    event_list = []

    try:
        results = CalendarEvent.get_all_events()
    except SQLAlchemyError:
        return -1

    if not results:
        return {}

    for r in results:
        event_list.append(json.loads(r.event))

    for event in event_list:
        user_id = str(event['event_info']['user_id'])
        event_type = event['type']
        event_info = event['event_info']

        if event_type == PREFERENCES_CREATED_EVENT:
            aggregate_status[user_id] = event_info

        elif event_type == PREFERENCES_MODIFIED_EVENT:
            aggregate_status[user_id]['preferences'] = event_info['preferences']

            global_preferences = aggregate_status[user_id]['preferences']

            if 'calendars' in aggregate_status[user_id]:
                for calendar in aggregate_status[user_id]['calendars'].values():
                    calendar['preferences'] = make_calendar_preferences_consistent(global_preferences,
                                                                                   calendar['preferences'])

        elif event_type == PREFERENCES_DELETED_EVENT:
            aggregate_status.pop(user_id)

        else:
            if 'calendars' not in aggregate_status[user_id].keys():
                aggregate_status[user_id].update(dict(calendars=dict()))

            id = str(event['event_info']['id'])
            event_info.pop('user_id', None)
            event_info.pop('id', None)

            if event_type == CALENDAR_CREATED_EVENT or event_type == CALENDAR_MODIFIED_EVENT:
                aggregate_status[user_id]['calendars'][id] = event_info

            elif event_type == CALENDAR_DELETED_EVENT:
                aggregate_status[user_id]['calendars'].pop(id)

    return aggregate_status
