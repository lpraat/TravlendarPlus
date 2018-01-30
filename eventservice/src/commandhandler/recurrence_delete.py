from flask import request, logging, jsonify
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.constants import RECURRENCE_DELETED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_event_aggregate
from src.eventrepository.data.event import EventEvent
from src.events.events import RecurrenceDeletedEvent
from src.responses import ko, not_found, ok
from src.utils import get_sending_channel

logger = logging.getLogger(__name__)


@command.route('/users/<int:user_id>/calendars/<int:calendar_id>/events/<int:event_id>/recurrences/<int:id>', methods=['DELETE'])
def handle_recurrence_delete(user_id, calendar_id, event_id, id):
    """
    This endpoint deletes a recurrence of an event.
    """
    aggregate_status = build_event_aggregate()

    if aggregate_status == -1:
        logger.error(f'Could not build calendar aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build calendar aggregate')))

    if not (str(user_id) in aggregate_status.keys()):
        return not_found(jsonify(dict(error='invalid user')))

    if not (str(calendar_id) in aggregate_status[str(user_id)]['calendars'].keys()):
        return not_found(jsonify(dict(error='invalid calendar')))

    if not (str(event_id) in aggregate_status[str(user_id)]['calendars'][str(calendar_id)]['events'].keys()):
        return not_found(jsonify(dict(error='invalid event')))

    if not(str(id) in aggregate_status[str(user_id)]['calendars'][str(calendar_id)]['events'][str(event_id)]['recurrences'].keys()):
        return not_found(jsonify(dict(error='invalid recurrence')))


    data = dict()
    data['user_id'] = user_id
    data['calendar_id'] = calendar_id
    data['event_id'] = event_id
    data['id'] = id

    event = RecurrenceDeletedEvent(**data)

    session = EventStoreSession()

    try:

        # both of these are wrapped inside a unique try catch because this must be an atomic operation.
        EventEvent.append_event(event)
        event_published = publish_event(get_sending_channel(), event, RECURRENCE_DELETED)

        if not event_published:
            logger.error(f'Could not publish event on event bus for request: {request}')
            session.rollback()
            return ko(jsonify(dict(error='could not publish event on event bus')))

        else:
            session.commit()
            logger.info(f'Deleted reccurece for user {user_id} on calendar id {calendar_id} on event id {event_id} with id {id}')
            return ok(jsonify(dict(user_id=user_id, calendar_id=calendar_id, id=id)))

    except SQLAlchemyError:
        session.rollback()
        logger.error(f'Could not append to event store for request: {request}')
        return ko(jsonify(dict(error='could not append to event store')))

    finally:
        session.close()
