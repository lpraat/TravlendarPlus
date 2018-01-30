import json
from uuid import uuid4 as uid

from src.constants import CALENDAR_ID_CREATED_EVENT, CALENDAR_ID_DELETED_EVENT, \
    EVENT_CREATED_EVENT, EVENT_MODIFIED_EVENT, EVENT_DELETED_EVENT, RECURRENCE_DELETED_EVENT, \
    USER_CALENDARS_DELETED_EVENT

"""
Here are defined the events used in the event sourcing by this micro service.
"""

def serialize_rule(x):
    return x.__dict__


generate_uuid = lambda: str(uid())


class Event(object):
    def __init__(self, type):
        self.uuid = generate_uuid()
        self.type = type

    def toJSON(self):
        return json.dumps(self, default=serialize_rule, indent=2)


class EventCreatedEvent(Event):
    def __init__(self, user_id, calendar_id, id, name, location, start_time, end_time, next_is_base, recurrence_rule,
                 until, flex,
                 flex_duration):
        super().__init__(EVENT_CREATED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            calendar_id=calendar_id,
            id=id,
            name=name,
            location=location,
            start_time=start_time,
            end_time=end_time,
            recurrence_rule=recurrence_rule,
            next_is_base=next_is_base,
            until=until,
            flex=flex,
            flex_duration=flex_duration
        )


class EventModifiedEvent(Event):
    def __init__(self, user_id, calendar_id, id, name, location, start_time, end_time, next_is_base, recurrence_rule,
                 until, flex,
                 flex_duration):
        super().__init__(EVENT_MODIFIED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            calendar_id=calendar_id,
            id=id,
            name=name,
            location=location,
            start_time=start_time,
            end_time=end_time,
            next_is_base=next_is_base,
            recurrence_rule=recurrence_rule,
            until=until,
            flex=flex,
            flex_duration=flex_duration
        )


class EventDeletedEvent(Event):
    def __init__(self, user_id, calendar_id, id):
        super().__init__(EVENT_DELETED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            calendar_id=calendar_id,
            id=id
        )


class RecurrenceDeletedEvent(Event):
    def __init__(self, user_id, calendar_id, event_id, id):
        super().__init__(RECURRENCE_DELETED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            calendar_id=calendar_id,
            event_id=event_id,
            id=id
        )


class CalendarIdCreatedEvent(Event):
    def __init__(self, uuid, user_id, id):
        super().__init__(CALENDAR_ID_CREATED_EVENT)
        self.uuid = uuid
        self.event_info = dict(
            user_id=user_id,
            id=id
        )


class CalendarIdDeletedEvent(Event):
    def __init__(self, uuid, user_id, id):
        super().__init__(CALENDAR_ID_DELETED_EVENT)
        self.uuid = uuid
        self.event_info = dict(
            user_id=user_id,
            id=id
        )


class UserCalendarsDeletedEvent(Event):
    def __init__(self, uuid, user_id):
        super().__init__(USER_CALENDARS_DELETED_EVENT)
        self.uuid = uuid
        self.event_info = dict(
            user_id=user_id,
        )
