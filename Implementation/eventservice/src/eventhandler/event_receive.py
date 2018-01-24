import json
import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from src.constants import \
    CALENDAR_CREATED_EVENT, EVENT_QUEUE, CALENDAR_ID_CREATED, CALENDAR_ID_CREATED_EVENT, CALENDAR_DELETED_EVENT, \
    CALENDAR_ID_DELETED, CALENDAR_ID_DELETED_EVENT, EVENT_CREATED_EVENT, EVENT_MODIFIED_EVENT, EVENT_DELETED_EVENT, \
    RECURRENCE_DELETED_EVENT, PREFERENCES_DELETED_EVENT, USER_CALENDARS_DELETED_EVENT, USER_CALENDARS_DELETED
from src.eventhandler.event_send import publish_event
from src.eventrepository import EventStoreSession
from src.eventrepository.data.event import EventEvent
from src.events.events import CalendarIdCreatedEvent, CalendarIdDeletedEvent, UserCalendarsDeletedEvent
from src.queryrepository.data.event import CalendarId, Recurrence
from src.queryrepository.data.event import Event
from src.queryrepository.update import add_calendar_id, delete_calendar_id, add_event, modify_event, delete_event, \
    delete_recurrence, delete_user_calendars
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

            # Events coming from calendar microservice

            if event_type == CALENDAR_CREATED_EVENT:
                add_and_publish_event(CalendarIdCreatedEvent(
                    event['uuid'], event_info['user_id'], event_info['id']), CALENDAR_ID_CREATED
                )

            elif event_type == CALENDAR_DELETED_EVENT:
                add_and_publish_event(CalendarIdDeletedEvent(
                    event['uuid'], event_info['user_id'], event_info['id']), CALENDAR_ID_DELETED
                )

            elif event_type == PREFERENCES_DELETED_EVENT:
                add_and_publish_event(UserCalendarsDeletedEvent(
                    event['uuid'], event_info['user_id']), USER_CALENDARS_DELETED
                )

            # Events generated in this microservice

            elif event_type == CALENDAR_ID_CREATED_EVENT:
                add_calendar_id(CalendarId(**event_info))

            elif event_type == CALENDAR_ID_DELETED_EVENT:
                delete_calendar_id(CalendarId(**event_info))

            elif event_type == USER_CALENDARS_DELETED_EVENT:
                delete_user_calendars(event_info['user_id'])

            elif event_type == EVENT_CREATED_EVENT:
                add_event(Event(**event_info))

            elif event_type == EVENT_MODIFIED_EVENT:
                modify_event(Event(**event_info))

            elif event_type == EVENT_DELETED_EVENT:
                delete_event(Event(**event_info))

            elif event_type == RECURRENCE_DELETED_EVENT:
                delete_recurrence(Recurrence(**event_info))


        except SQLAlchemyError as e:

            # to deal with at least once delivery of rabbitmq and the create methods which are not idempotent
            if (event_type == CALENDAR_CREATED_EVENT or event_type == CALENDAR_ID_CREATED_EVENT) \
                    and method.redelivered and isinstance(e, IntegrityError):
                logger.info(f'Not processed redelivered event {event}')

            else:
                logger.info(f"Couldn't process event {event}")
                success = False
                raise e

        finally:
            if success:  # ack only if the event has been processed
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Processed and acked event {event}")

    # channel.basic_qos(prefetch_count=1)
    channel.basic_consume(callback,
                          queue=EVENT_QUEUE)

    logger.info("Started listening to events")
    channel.start_consuming()


# adds the event to the event store and publish it on the event bus
def add_and_publish_event(event, routing_key):
    """
    Adds the event to the event store and publish it on the event bus.
    :param event: the event.
    :param routing_key: the routing key for topic-matching.
    """
    session = EventStoreSession()

    try:

        # both of these are wrapped inside a unique try catch because this must be an atomic operation.
        EventEvent.append_event(event)
        event_published = publish_event(get_sending_channel(), event, routing_key)

        if not event_published:
            logger.error(f'Could not publish event {event.toJSON()}')
            session.rollback()
            raise SQLAlchemyError

        else:
            session.commit()
            logger.info(f'Added and published event {event.toJSON()}')

    except SQLAlchemyError:
        session.rollback()
        logger.error(f'Could not append to event store event {event.toJSON()}')
        raise SQLAlchemyError

    finally:
        session.close()
