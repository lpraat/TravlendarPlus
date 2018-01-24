import logging

from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.constants import USER_DELETED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_user_aggregate
from src.eventrepository.data.event import UserEvent
from src.events.events import UserDeletedEvent
from src.responses import ko, ok, not_found
from src.utils import get_sending_channel

logger = logging.getLogger(__name__)


@command.route('/users/<int:user_id>', methods=['DELETE'])
def handle_delete(user_id):

    """
    Delete user endpoint. It deletes a user resource.
    """
    aggregate_status = build_user_aggregate()

    if aggregate_status == -1:
        logger.error(f'Could not build user aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build user aggregate')))

    if not (str(user_id) in aggregate_status.keys()):
        return not_found(jsonify(dict(error='invalid user')))

    event = UserDeletedEvent(id=user_id)

    session = EventStoreSession()
    try:
        UserEvent.append_event(event)
        event_published = publish_event(get_sending_channel(), event, USER_DELETED)

        if not event_published:
            logger.error(f'Could not publish event on event bus for request: {request}')
            session.rollback()
            return ko(jsonify(dict(error='could not publish event on event bus')))

        else:
            session.commit()
            logger.info(f'Deleted user with id: {user_id}')
            return ok(jsonify(dict(id=user_id)))

    except SQLAlchemyError:
        session.rollback()
        logger.error(f'Could not append to event store for request: {request}')
        return ko(jsonify(dict(error='could not append to event store')))

    finally:
        session.close()

