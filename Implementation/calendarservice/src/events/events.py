import json
from uuid import uuid4 as uid

from src.constants import CALENDAR_CREATED_EVENT, PREFERENCES_CREATED_EVENT, PREFERENCES_DELETED_EVENT, \
    CALENDAR_MODIFIED_EVENT, CALENDAR_DELETED_EVENT, PREFERENCES_MODIFIED_EVENT

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
        return json.dumps(self, default=serialize_rule)


class CalendarCreatedEvent(Event):
    def __init__(self, user_id, id, name, description, base, color, active, carbon, preferences):
        super().__init__(CALENDAR_CREATED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            id=id,
            name=name,
            description=description,
            base=base,
            color=color,
            active=active,
            carbon=carbon,
            preferences=preferences
        )


class CalendarModifiedEvent(Event):
    def __init__(self, user_id, id, name, description, base, color, active, carbon, preferences):
        super().__init__(CALENDAR_MODIFIED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            id=id,
            name=name,
            description=description,
            base=base,
            color=color,
            active=active,
            carbon=carbon,
            preferences=preferences
        )


class CalendarDeletedEvent(Event):
    def __init__(self, user_id, id):
        super().__init__(CALENDAR_DELETED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            id=id
        )


class GlobalPreferencesCreatedEvent(Event):
    def __init__(self, uuid, user_id, preferences):
        super().__init__(PREFERENCES_CREATED_EVENT)
        self.uuid = uuid
        self.event_info = dict(
            user_id=user_id,
            preferences=preferences
        )


class GlobalPreferencesModifiedEvent(Event):
    def __init__(self, user_id, preferences):
        super().__init__(PREFERENCES_MODIFIED_EVENT)
        self.event_info = dict(
            user_id=user_id,
            preferences=preferences
        )


class GlobalPreferencesDeletedEvent(Event):
    def __init__(self, uuid, user_id):
        super().__init__(PREFERENCES_DELETED_EVENT)
        self.uuid = uuid
        self.event_info = dict(
            user_id=user_id
        )
