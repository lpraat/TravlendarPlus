from flask import request, logging, jsonify
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.commandhandler.validate_data import validate_event, event_can_be_inserted
from src.constants import EVENT_CREATED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_event_aggregate
from src.eventrepository.data.event import EventEvent
from src.events.events import EventCreatedEvent
from src.responses import ko, not_found, bad_request, created
from src.utils import get_sending_channel

logger = logging.getLogger(__name__)


@command.route('/users/<int:user_id>/calendars/<int:calendar_id>/events', methods=['POST'])
def handle_create(user_id, calendar_id):
    """
    This endpoint creates a new event resource
    """
    data = request.get_json()
    aggregate_status = build_event_aggregate()

    if aggregate_status == -1:
        logger.error(f'Could not build calendar aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build calendar aggregate')))

    if not (str(user_id) in aggregate_status.keys()):
        return not_found(jsonify(dict(error='invalid user')))

    if not (str(calendar_id) in aggregate_status[str(user_id)]['calendars'].keys()):
        return not_found(jsonify(dict(error='invalid calendar')))

    user_schedule = aggregate_status[str(user_id)]['calendars']

    # checks if the request payload is formed correctly and if the event can be inserted in the user schedule
    # given the current aggregate status
    if validate_event(data) and event_can_be_inserted(data, user_schedule):
        calendar_events = aggregate_status[str(user_id)]['calendars'][str(calendar_id)]['events']
        if not calendar_events:
            new_id = 1
        else:
            new_id = int(max(calendar_events, key=int)) + 1

        if 'until' not in data:
            data['until'] = None

        if 'flex' not in data:
            data['flex'] = None
            data['flex_duration'] = None

        data['user_id'] = user_id
        data['calendar_id'] = calendar_id
        data['id'] = new_id

        event = EventCreatedEvent(**data)

        session = EventStoreSession()

        try:
            # both of these are wrapped inside a unique try catch because this must be an atomic operation.
            EventEvent.append_event(event)
            event_published = publish_event(get_sending_channel(), event, EVENT_CREATED)

            if not event_published:
                logger.error(f'Could not publish event on event bus for request: {request}')
                session.rollback()
                return ko(jsonify(dict(error='could not publish event on event bus')))

            else:
                session.commit()
                logger.info(f'Created event for user {user_id} on calendar id {calendar_id} with id {new_id}')
                return created(jsonify(dict(user_id=user_id, calendar_id=calendar_id, id=new_id)))

        except SQLAlchemyError:
            session.rollback()
            logger.error(f'Could not append to event store for request: {request}')
            return ko(jsonify(dict(error='could not append to event store')))

        finally:
            session.close()

    return bad_request(jsonify(dict(error='invalid data')))
