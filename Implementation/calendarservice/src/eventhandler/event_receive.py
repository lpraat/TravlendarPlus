import json
import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.constants import PREFERENCES_CREATED_EVENT, USER_CREATED_EVENT, CALENDAR_QUEUE, \
    PREFERENCES_CREATED, USER_DELETED_EVENT, PREFERENCES_DELETED_EVENT, PREFERENCES_DELETED, PREFERENCES_MODIFIED_EVENT, \
    CALENDAR_CREATED_EVENT, CALENDAR_MODIFIED_EVENT, CALENDAR_DELETED_EVENT
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent, GlobalPreferencesDeletedEvent
from src.queryrepository.data.calendar import Calendar
from src.queryrepository.data.calendar import GlobalPreferences
from src.queryrepository.update import add_global_preferences, modify_global_preferences, delete_global_preferences, \
    add_calendar, modify_calendar, delete_calendar
from src.utils import get_sending_channel

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
            # Events coming from account microservice

            if event_type == USER_CREATED_EVENT:

                add_and_publish_event(
                    GlobalPreferencesCreatedEvent(event['uuid'], event_info['id'], dict(
                        vehicles=['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi',
                                  'enjoy', 'mobike'],
                        personal_vehicles=[])),
                    PREFERENCES_CREATED)

            elif event_type == USER_DELETED_EVENT:

                add_and_publish_event(GlobalPreferencesDeletedEvent(event['uuid'], event_info['id']), PREFERENCES_DELETED)

            # Events generated in this microservice

            elif event_type == PREFERENCES_CREATED_EVENT:
                add_global_preferences(GlobalPreferences(**event_info))

            elif event_type == PREFERENCES_MODIFIED_EVENT:
                modify_global_preferences(GlobalPreferences(**event_info))

            elif event_type == PREFERENCES_DELETED_EVENT:
                delete_global_preferences(GlobalPreferences(**event_info))

            elif event_type == CALENDAR_CREATED_EVENT:
                add_calendar(Calendar(**event_info))

            elif event_type == CALENDAR_MODIFIED_EVENT:
                modify_calendar(Calendar(**event_info))

            elif event_type == CALENDAR_DELETED_EVENT:
                delete_calendar(Calendar(**event_info))

        except SQLAlchemyError as e:

            # to deal with at least once delivery of rabbitmq and the create methods which are not idempotent
            if (event_type == USER_CREATED_EVENT or event_type == PREFERENCES_CREATED_EVENT or event_type == CALENDAR_CREATED_EVENT) \
                    and method.redelivered and isinstance(e, IntegrityError):
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
                          queue=CALENDAR_QUEUE)

    logger.info("Started listening to events")
    channel.start_consuming()


def add_and_publish_event(event, routing_key):
    """
    Adds the event to the event store and publish it on the event bus.
    :param event: the event.
    :param routing_key: the routing key for topic-matching.
    """
    session = EventStoreSession()

    try:
        # both of these are wrapped inside a unique try catch because this must be an atomic operation.
        CalendarEvent.append_event(event)
        event_published = publish_event(get_sending_channel(), event, routing_key)

        if not event_published: # message cannot be routed
            logger.error(f'Could not publish event {event.toJSON()}')
            session.rollback()
            raise SQLAlchemyError

        else:
            session.commit()
            logger.info(f'Added and published event {event.toJSON()}')

    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f'Could not append to event store event {event.toJSON()}')
        raise e

    finally:
        session.close()
