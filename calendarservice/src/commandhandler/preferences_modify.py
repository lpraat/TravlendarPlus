import logging

from flask import request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.commandhandler.validate_data_preferences import validate_global_preferences
from src.constants import PREFERENCES_MODIFIED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_calendar_aggregate
from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesModifiedEvent
from src.responses import bad_request, ko, not_found, ok
from src.utils import get_sending_channel

logger = logging.getLogger(__name__)


@command.route('/users/<int:user_id>/preferences', methods=['PUT'])
def handle_preferences(user_id):
    """
    Global preferences modify endpoint. It modifies user global preferences.
    """
    aggregate_status = build_calendar_aggregate()

    if aggregate_status == -1:
        logger.error(f'Could not build user aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build user aggregate')))

    if not (str(user_id) in aggregate_status.keys()):
        return not_found(jsonify(dict(error='invalid user')))

    data = request.get_json()

    if validate_global_preferences(data):  # checks the request payload is correctly formed

        event = GlobalPreferencesModifiedEvent(user_id=user_id, preferences=data)
        session = EventStoreSession()

        try:

            # both of these are wrapped inside a unique try catch because this must be an atomic operation.
            CalendarEvent.append_event(event)
            event_published = publish_event(get_sending_channel(), event, PREFERENCES_MODIFIED)

            if not event_published:
                logger.error(f'Could not publish event on event bus for request: {request}')
                session.rollback()
                return ko(jsonify(dict(error='could not publish event on event bus')))

            else:
                session.commit()
                logger.info(f'Modified global preferences of user with id: {user_id}')
                return ok(jsonify(dict(id=user_id)))

        except SQLAlchemyError:
            session.rollback()
            logger.error(f'Could not append to event store for request: {request}')
            return ko(jsonify(dict(error='could not append to event store')))

        finally:
            session.close()

    return bad_request(jsonify(dict(error='invalid data')))
