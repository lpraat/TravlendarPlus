import json

from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler.validate_data import RRULE
from src.constants import CALENDAR_ID_CREATED_EVENT, CALENDAR_ID_DELETED_EVENT, EVENT_CREATED_EVENT, \
    EVENT_MODIFIED_EVENT, EVENT_DELETED_EVENT, USER_CALENDARS_DELETED_EVENT
from src.eventrepository.data.event import EventEvent
from src.utils import generate_occurrences, strptime


def build_event_aggregate():
    """
    This builds the event aggregate by chronologically applying events in the event store.
    :return: the aggregate status.
    """
    aggregate_status = {}
    event_list = []

    try:
        results = EventEvent.get_all_events()
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

        if event_type == CALENDAR_ID_CREATED_EVENT:

            if user_id not in aggregate_status:
                aggregate_status[user_id] = \
                    {'calendars': {}}

            aggregate_status[user_id]['calendars'].update({str(event_info['id']): {'events': {}}})

        elif event_type == CALENDAR_ID_DELETED_EVENT:
            aggregate_status[user_id]['calendars'].pop(str(event_info['id']))

        elif event_type == USER_CALENDARS_DELETED_EVENT:
            try:
                aggregate_status.pop(user_id)
            except KeyError:
                pass  # user had no calendars

        else:
            calendar_id = str(event_info['calendar_id'])
            event_id = str(event_info['id'])

            if event_type == EVENT_CREATED_EVENT or event_type == EVENT_MODIFIED_EVENT:

                event_info.pop('user_id')
                event_info.pop('calendar_id')
                event_info.pop('id')
                event_info['start_time'] = strptime(event_info['start_time'])
                event_info['end_time'] = strptime((event_info['end_time']))

                aggregate_status[user_id]['calendars'][calendar_id]['events'].update(
                    {
                        event_id: {
                            **event_info,
                            'recurrences': {}
                        }
                    })

                start_time = event_info['start_time']
                end_time = event_info['end_time']

                if event_info['recurrence_rule'] == 'NORMAL':
                    aggregate_status[user_id]['calendars'][calendar_id]['events'][event_id]['recurrences'].update({
                        '1': dict(
                            start_time=start_time,
                            end_time=end_time
                        )
                    })
                else:
                    rec_rule = event_info['recurrence_rule']
                    until = strptime(event_info['until'])
                    start_occurrences, end_occurrences = generate_occurrences(RRULE[rec_rule]['name'], start_time,
                                                                              end_time,
                                                                              until)

                    for index, (s_time, e_time) in enumerate(zip(start_occurrences, end_occurrences), 1):
                        aggregate_status[user_id]['calendars'][calendar_id]['events'][event_id]['recurrences'].update({
                            str(index): {
                                'start_time': s_time,
                                'end_time': e_time
                            }
                        })

            elif event_type == EVENT_DELETED_EVENT:
                aggregate_status[user_id]['calendars'][calendar_id]['events'].pop(event_id)

    return aggregate_status
