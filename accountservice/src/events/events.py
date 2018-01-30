import json
from uuid import uuid4 as uid

from src.constants import USER_CREATED_EVENT, USER_MODIFIED_EVENT, USER_DELETED_EVENT

"""
Here are defined the events used in the event sourcing by this micro service.
"""

generate_uuid = lambda: str(uid())


class Event(object):
    def __init__(self, type):
        self.uuid = generate_uuid()
        self.type = type

    def toJSON(self):
        return json.dumps(self, default=lambda x: x.__dict__, indent=2)


class UserCreatedEvent(Event):
    def __init__(self, id, email, password, first_name, last_name):
        super().__init__(USER_CREATED_EVENT)
        self.event_info = dict(
            id=id,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )


class UserModifiedEvent(Event):
    def __init__(self, id, email, password, first_name, last_name):
        super().__init__(USER_MODIFIED_EVENT)
        self.event_info = dict(
            id=id,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )


class UserDeletedEvent(Event):
    def __init__(self, id):
        super().__init__(USER_DELETED_EVENT)
        self.event_info = dict(
            id=id
        )
