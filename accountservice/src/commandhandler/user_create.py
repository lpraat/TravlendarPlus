import logging

import requests
from flask import jsonify
from flask import request
from sqlalchemy.exc import SQLAlchemyError

from src.commandhandler import command
from src.commandhandler.validate_data import validate_request_payload, validate_user_data, is_unique_email
from src.configs import KONG_IP
from src.constants import USER_CREATED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.aggregate_builder import build_user_aggregate
from src.eventrepository.data.event import UserEvent
from src.events.events import UserCreatedEvent
from src.responses import created, ko, bad_request
from src.utils import get_sending_channel
from src.utils import hash_pass

logger = logging.getLogger(__name__)

KONG_CONSUMER_API = f"http://{KONG_IP}:8001/consumers"


@command.route('/users', methods=['POST'])
def handle_create():
    """
    This is the create user endpoint. It creates a new user resource.
    """
    data = request.get_json()

    aggregate_status = build_user_aggregate()
    if aggregate_status == -1:
        logger.error(f'Could not build user aggregate for request: {request}')
        return ko(jsonify(dict(error='cannot build user aggregate')))

    if validate_request_payload(data):  # checks the data in the payload is formed correctly
        email = data['email']
        password = data['password']
        first_name = data['first_name']
        last_name = data['last_name']
        logger.info("Validated request payload")
        if validate_user_data(email, password, first_name, last_name):
            logger.info("Validated user data")

            # checks if the account can be created given the current aggregate status
            if is_unique_email(email, aggregate_status):
                logger.info("Email is indeed unique")
                if aggregate_status:
                    new_id = int(max(aggregate_status, key=int)) + 1
                else:
                    new_id = 1

                data['id'] = new_id
                data['password'] = hash_pass(password)

                event = UserCreatedEvent(**data)

                session = EventStoreSession()

                logger.info(data)
                try:

                    # both of these are wrapped inside a unique try catch because this must be an atomic operation.
                    UserEvent.append_event(event)
                    event_published = publish_event(get_sending_channel(), event, USER_CREATED)

                    # create a new consumer inside kong
                    kong_request = requests.post(KONG_CONSUMER_API, data={'username': email})
                    if not event_published or not kong_request.status_code == 201:
                        logger.error(f'Could not publish event on event bus for request: {request}')
                        session.rollback()
                        return ko(jsonify(dict(error='could not publish event on event bus')))

                    else:
                        session.commit()
                        logger.info(f'Created user with id: {new_id}')
                        logger.info(f"Added new consumer to kong with username {email}")
                        return created(jsonify(dict(id=new_id)))

                except SQLAlchemyError:
                    session.rollback()
                    logger.error(f'Could not append to event store for request: {request}')
                    return ko(jsonify(dict(error='could not append to event store')))

                except Exception as e:
                    logger.error(e)
                finally:
                    session.close()

    return bad_request(jsonify(dict(error='invalid data')))
