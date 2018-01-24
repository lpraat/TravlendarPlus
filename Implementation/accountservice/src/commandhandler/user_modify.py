import logging

from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.commandhandler.validate_data import validate_request_payload, is_unique_email, validate_user_data
from src.constants import USER_MODIFIED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_user_aggregate
from src.eventrepository.data.event import UserEvent
from src.events.events import UserModifiedEvent
from src.responses import ko, not_found, ok, bad_request
from src.utils import get_sending_channel
from src.utils import hash_pass

logger = logging.getLogger(__name__)


@command.route('/users/<int:user_id>', methods=['PUT'])
def handle_modify(user_id):

    """
    Modify user endpoint. It modifies a user resource.
    """
    aggregate_status = build_user_aggregate()

    if aggregate_status == -1:
        logger.error(f'Could not build user aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build user aggregate')))

    if not (str(user_id) in aggregate_status.keys()):
        return not_found(jsonify(dict(error='invalid user')))

    data = request.get_json()

    if validate_request_payload(data):
        email = data['email']
        password = data['password']
        first_name = data['first_name']
        last_name = data['last_name']

        aggregate_status.pop(str(user_id))  # pops the current email to preserve idempotency

        if validate_user_data(email, password, first_name, last_name):

            if is_unique_email(email, aggregate_status):

                data['id'] = user_id
                data['password'] = hash_pass(data['password'])

                event = UserModifiedEvent(**data)

                session = EventStoreSession()

                try:

                    # both of these are wrapped inside a unique try catch because this must be an atomic operation.
                    UserEvent.append_event(event)
                    event_published = publish_event(get_sending_channel(), event, USER_MODIFIED)

                    if not event_published:
                        logger.error(f'Could not publish event on event bus for request: {request}')
                        session.rollback()
                        return ko(jsonify(dict(error='could not publish event on event bus')))

                    else:
                        session.commit()
                        logger.info(f'Modified user with id: {user_id}')
                        return ok(jsonify(dict(id=user_id)))

                except SQLAlchemyError:
                    session.rollback()
                    logger.error(f'Could not append to event store for request: {request}')
                    return ko(jsonify(dict(error='could not append to event store')))

                finally:
                    session.close()

    return bad_request(jsonify(dict(error='invalid data')))
