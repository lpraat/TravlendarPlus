import json
import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.constants import USER_CREATED_EVENT, USER_MODIFIED_EVENT, USER_DELETED_EVENT, ACCOUNT_QUEUE
from src.queryrepository.data.user import User
from src.queryrepository.update import add_user, modify_user, delete_user

logger = logging.getLogger(__name__)


def receive(channel):
    """
    Listens to events coming from channel and process them properly.
    This function keeps consistent the query side according to what happened in the command side.
    It translates event store generated events into query-database.

    :param channel: the channel listening to.
    """

    def callback(ch, method, properties, body):
        event = json.loads(body)
        event_info = event['event_info']
        event_type = event['type']
        success = True
        logger.info(f"Received event {event}")

        try:

            if event_type == USER_CREATED_EVENT:
                add_user(User(**event_info))

            elif event_type == USER_MODIFIED_EVENT:
                modify_user(User(**event_info))

            elif event_type == USER_DELETED_EVENT:
                delete_user(User(**event_info))

        except SQLAlchemyError as e:

            # to deal with at least once delivery of rabbitmq and the create_user method which is not idempotent
            if event_type == USER_CREATED_EVENT and method.redelivered and isinstance(e, IntegrityError):
                logger.info(f'Not processed redelivered event {event}')

            else:
                logger.info(f"Couldn't process event {event}")
                success = False

        finally:
            if success:  # ack only if the event has been processed
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Processed and acked event {event}")

    # channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue=ACCOUNT_QUEUE)

    logger.info("Started listening to events")
    channel.start_consuming()
