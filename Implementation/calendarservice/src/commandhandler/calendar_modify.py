import logging

from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.commandhandler.validate_data_calendar import validate_calendar_data, validate_calendar_preferences
from src.constants import CALENDAR_MODIFIED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_calendar_aggregate
from src.eventrepository.data.event import CalendarEvent
from src.events.events import CalendarModifiedEvent
from src.responses import ko, not_found, bad_request, ok
from src.utils import get_sending_channel

logger = logging.getLogger(__name__)


@command.route('/users/<int:user_id>/calendars/<int:id>', methods=['PUT'])
def handle_modify(user_id, id):
    """
    Calendar modify endpoint. It modifies a calendar resource.
    """
    data = request.get_json()
    aggregate_status = build_calendar_aggregate()

    if aggregate_status == -1:
        logger.error(f'Could not build calendar aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build calendar aggregate')))

    if not (str(user_id) in aggregate_status.keys()):
        return not_found(jsonify(dict(error='invalid user')))

    if not (str(id) in aggregate_status[str(user_id)]['calendars'].keys()):
        return not_found(jsonify(dict(error='invalid calendar')))

    user_global_preferences = aggregate_status[str(user_id)]['preferences']

    # validate the request payload and check if the preferences are applicable given the global one
    # in the current aggregate status
    if validate_calendar_data(data) and validate_calendar_preferences(data['preferences'], user_global_preferences):

        user_calendars = aggregate_status[str(user_id)]['calendars']

        user_calendars.pop(str(id))  # pop for preserving idempotency

        if data['name'] in ((value['name'] for value in user_calendars.values())):
            return bad_request(jsonify(dict(error='invalid data')))

        data['user_id'] = user_id
        data['id'] = id

        event = CalendarModifiedEvent(**data)

        session = EventStoreSession()

        try:

            # both of these are wrapped inside a unique try catch because this must be an atomic operation.
            CalendarEvent.append_event(event)
            event_published = publish_event(get_sending_channel(), event, CALENDAR_MODIFIED)

            if not event_published:
                logger.error(f'Could not publish event on event bus for request: {request}')
                session.rollback()
                return ko(jsonify(dict(error='could not publish event on event bus')))

            else:
                session.commit()
                logger.info(f'Modified calendar for user {user_id} with id: {id}')
                return ok(jsonify(dict(user_id=user_id, id=id)))

        except SQLAlchemyError:
            session.rollback()
            logger.error(f'Could not append to event store for request: {request}')
            return ko(jsonify(dict(error='could not append to event store')))

        finally:
            session.close()

    return bad_request(jsonify(dict(error='invalid data')))
