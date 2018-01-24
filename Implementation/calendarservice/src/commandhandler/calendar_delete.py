import logging

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.constants import CALENDAR_DELETED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_calendar_aggregate
from src.eventrepository.data.event import CalendarEvent
from src.events.events import CalendarDeletedEvent
from src.responses import ko, not_found, ok
from src.utils import get_sending_channel

logger = logging.getLogger(__name__)


@command.route('/users/<int:user_id>/calendars/<int:id>', methods=['DELETE'])
def handle_delete(user_id, id):
    """
    Delete calendar endpoint. It deletes a calendar.
    """
    aggregate_status = build_calendar_aggregate()

    if aggregate_status == -1:
        logger.error(f'Could not build calendar aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build calendar aggregate')))

    if not (str(user_id) in aggregate_status.keys()):
        return not_found(jsonify(dict(error='invalid user')))

    if not (str(id) in aggregate_status[str(user_id)]['calendars'].keys()):
        return not_found(jsonify(dict(error='invalid calendar')))

    event = CalendarDeletedEvent(user_id=user_id, id=id)

    session = EventStoreSession()

    try:

        # both of these are wrapped inside a unique try catch because this must be an atomic operation.
        CalendarEvent.append_event(event)
        event_published = publish_event(get_sending_channel(), event, CALENDAR_DELETED)

        if not event_published:
            logger.error(f'Could not publish event on event bus for request: {request}')
            session.rollback()
            return ko(jsonify(dict(error='could not publish event on event bus')))

        else:
            session.commit()
            logger.info(f'Deleted calendar for user {user_id} with id: {id}')
            return ok(jsonify(dict(user_id=user_id, id=id)))

    except SQLAlchemyError:
        session.rollback()
        logger.error(f'Could not append to event store for request: {request}')
        return ko(jsonify(dict(error='could not append to event store')))

    finally:
        session.close()
