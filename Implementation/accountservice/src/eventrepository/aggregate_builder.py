import json

from sqlalchemy.exc import SQLAlchemyError

from src.constants import USER_CREATED_EVENT, USER_MODIFIED_EVENT, USER_DELETED_EVENT
from src.eventrepository.data.event import UserEvent


def build_user_aggregate():
    """
    This builds the user aggregate by chronologically applying events in the event store.
    :return: the aggregate status.
    """
    aggregate_status = {}
    event_list = []

    try:
        results = UserEvent.get_all_events()
    except SQLAlchemyError:
        return -1

    if not results:
        return {}

    for r in results:
        event_list.append(json.loads(r.event))

    for event in event_list:
        if event['type'] == USER_CREATED_EVENT or event['type'] == USER_MODIFIED_EVENT:
            aggregate_status[str(event['event_info']['id'])] = event['event_info']

        elif event['type'] == USER_DELETED_EVENT:
            aggregate_status.pop(str(event['event_info']['id']))

    return aggregate_status
