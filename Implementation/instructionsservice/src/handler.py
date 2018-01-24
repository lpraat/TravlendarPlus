import json
import logging
import threading
import time
from os import environ as env

import pika
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm.exc import UnmappedError

from instructions import yield_recurrences, calculate_instruction, fix_return_instruction, update_event_instructions
from models import db, Calendar, GlobalPreference, Overview
from queries import get_all_daily, get_incoming_daily, get_all_sorted, get_all_recurrences

logger = logging.getLogger(__name__)

RABBITMQ_IP = env['RABBITMQ_IP'] if 'RABBITMQ_IP' in env else 'localhost'
RABBITMQ_PORT = int(env['RABBITMQ_PORT']) if 'RABBITMQ_PORT' in env else 5672

INSTRUCTIONS_QUEUE = 'instructionsservice'
# Routing keys and exchanges
INSTRUCTIONS_EXCHANGE = 'instructions'
INSTRUCTION = "instruction.*"
INSTRUCTION_CREATED = 'instruction.created'
INSTRUCTION_MODIFIED = 'instruction.modified'
INSTRUCTION_DELETED = 'instruction.deleted'
CALENDAR_EXCHANGE = "calendar"
CALENDAR_CREATED = "calendar.created"
CALENDAR_MODIFIED = "calendar.modified"
CALENDAR_DELETED = "calendar.deleted"
PREFERENCES_CREATED = 'calendar.preferences.created'
PREFERENCES_MODIFIED = 'calendar.preferences.modified'
PREFERENCES_DELETED = 'calendar.preferences.deleted'
EVENT_EXCHANGE = 'event'
EVENT_CREATED = 'event.event.created'
EVENT_MODIFIED = 'event.event.modified'
EVENT_DELETED = 'event.event.deleted'
RECURRENCE_DELETED = 'event.recurrence.deleted'
# Events
EVENT_CREATED_EVENT = 'event_created_event'
EVENT_MODIFIED_EVENT = 'event_modified_event'
EVENT_DELETED_EVENT = 'event_deleted_event'
RECURRENCE_DELETED_EVENT = 'recurrence_deleted_event'
CALENDAR_CREATED_EVENT = 'calendar_created_event'
CALENDAR_MODIFIED_EVENT = 'calendar_modified_event'
CALENDAR_DELETED_EVENT = 'calendar_deleted_event'
PREFERENCES_CREATED_EVENT = 'preferences_created_event'
PREFERENCES_MODIFIED_EVENT = 'preferences_modified_event'
PREFERENCES_DELETED_EVENT = 'preferences_deleted_event'


def create_connection(ip, port):
    return pika.BlockingConnection(pika.ConnectionParameters(host=ip, port=port))


def setup_sending_channel(app_ctx=True, exchange=INSTRUCTIONS_EXCHANGE, queue=INSTRUCTIONS_QUEUE):
    connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
    channel = connection.channel()

    channel.exchange_declare(exchange=exchange, exchange_type='topic')
    channel.queue_declare(queue=queue, durable=True)

    channel.confirm_delivery()

    if app_ctx:
        def send_heartbeats():
            while True:
                time.sleep(2)
                connection.process_data_events()

        t = threading.Thread(target=send_heartbeats)
        t.daemon = True
        t.start()

    return channel


def setup_receiving_channel():
    connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
    channel = connection.channel()
    exchanges = {
        INSTRUCTIONS_EXCHANGE: [INSTRUCTION],
        CALENDAR_EXCHANGE: [CALENDAR_CREATED, CALENDAR_MODIFIED, CALENDAR_DELETED,
                            PREFERENCES_CREATED, PREFERENCES_MODIFIED, PREFERENCES_DELETED],
        EVENT_EXCHANGE: [EVENT_CREATED, EVENT_MODIFIED, EVENT_DELETED, RECURRENCE_DELETED]
    }
    channel.queue_declare(queue=INSTRUCTIONS_QUEUE, durable=True)  # declare queue for this service
    for exchange, routing_keys in exchanges.items():
        for routing_key in routing_keys:
            channel.exchange_declare(exchange=exchange, exchange_type='topic')
            channel.queue_bind(exchange=exchange,  # bind the queue to each exchange with all subscribed routing keys
                               queue=INSTRUCTIONS_QUEUE,
                               routing_key=routing_key)
    return channel


def get_sending_channel():
    if not current_app:
        return setup_sending_channel(app_ctx=False)
    return current_app.sending_channel


def receive(channel, app):
    mapping = {  # maps each message to the corresponding handling function
        EVENT_CREATED_EVENT: handle_event_create,
        EVENT_MODIFIED_EVENT: handle_event_modify,
        EVENT_DELETED_EVENT: handle_event_delete,
        CALENDAR_CREATED_EVENT: handle_calendar_create,
        CALENDAR_MODIFIED_EVENT: handle_calendar_modify,
        CALENDAR_DELETED_EVENT: handle_calendar_delete,
        PREFERENCES_CREATED_EVENT: handle_preferences_create,
        PREFERENCES_MODIFIED_EVENT: handle_preferences_modify,
        PREFERENCES_DELETED_EVENT: handle_preferences_delete,
        RECURRENCE_DELETED_EVENT: handle_recurrence_delete
    }

    def callback(ch, method, properties, body):
        event = json.loads(body)
        success = True
        logger.info(f"Received event {event}")
        try:
            mapping[event['type']](event['event_info'])  # calls proper handling function

        except KeyError as e:
            logger.error(f"No function associated for event of type {event['type']}")
            logger.error(e)
        except SQLAlchemyError as e:
            logger.info(f"Couldn't process event {event}")
            logger.error(e)
            db.session.rollback()  # restores to previous state
            success = False

        finally:
            if success:  # ack only if the event has been processed
                ch.basic_ack(delivery_tag=method.delivery_tag)
                logger.info(f"Processed and acked event {event}")

    channel.basic_consume(callback,
                          queue=INSTRUCTIONS_QUEUE)
    logger.info("Started listening to events")
    app.app_context().push()  # pushes app context for new thread
    channel.start_consuming()


def publish_event(channel, exchange, event, routing_key):
    logging.info(f"Published event: {event}")
    return channel.basic_publish(exchange=exchange,
                                 routing_key=routing_key,
                                 mandatory=True,  # basic publish returns false if there is no queue that routes the msg
                                 properties=pika.BasicProperties(delivery_mode=2),
                                 body=event)


def handle_event_create(info):
    global_preferences = GlobalPreference.query.get(info['user_id'])
    calendar_pk = (info['calendar_id'], info['user_id'])
    calendar = Calendar.query.get(calendar_pk)
    for recurrence_id, event in enumerate(yield_recurrences(info), start=1):
        calculate_instruction(global_preferences, calendar, event, recurrence_id)


def handle_event_modify(info):
    logger.info(f"Modifying event {info}")
    user_id = info['user_id']
    global_preferences = GlobalPreference.query.get(user_id)
    calendar_pk = (info['calendar_id'], user_id)
    calendar = Calendar.query.get(calendar_pk)
    overviews = get_all_recurrences(info, user_id=user_id)
    recurrences = list(yield_recurrences(info))
    for i, overview in enumerate(overviews):  # modify all overviews
        update_event_instructions(global_preferences, calendar, overview, **recurrences[i])


def handle_event_delete(info, recurrence_id=None):
    logger.info(info)
    user_id = info['user_id']
    calendar_id = info['calendar_id']
    event_id = info['id']
    global_preferences = GlobalPreference.query.get(user_id)
    calendar = Calendar.query.get((calendar_id, user_id))
    if recurrence_id:
        overviews = [Overview.query.get((recurrence_id, user_id, calendar_id, event_id, True))]
    else:
        overviews = get_all_recurrences(info, user_id)
    for overview in overviews:
        db.session.delete(overview)
        db.session.commit()
        logger.info(f"Deleted overview {overview}")
        all_daily = get_all_daily(user_id, overview.start_date, departure_only=True)
        incoming_daily = get_incoming_daily(user_id, overview.start_date)
        if not incoming_daily:  # this was the last event of the day, need to handle return overview
            new_last = max(all_daily, key=lambda o: o.start_date) if all_daily else overview
            # we are inserting a new return overview only if there exist other instructions on the same day AND
            # the user requested information for going back after this event
            fix_return_instruction(global_preferences, calendar, new_last.start_date, new_last.event_id, new_last.id,
                                   insert_new=bool(all_daily) and overview.next_is_base)
        else:  # Need to update instructions for the very next event
            next_event = min(incoming_daily, key=lambda o: o.start_date)
            update_event_instructions(global_preferences, calendar, next_event)


def handle_recurrence_delete(info):
    handle_event_delete(info, recurrence_id=info['id'])


def handle_calendar_create(info):
    calendar = Calendar(**info)
    db.session.add(calendar)
    db.session.commit()
    logger.info(f"Created calendar with key: {(info['id'], info['user_id'])}")


def handle_calendar_modify(info):
    try:
        primary_key = (info['id'], info['user_id'])
        calendar = Calendar.query.get(primary_key)
        for k, v in info.items():
            setattr(calendar, k, v)
        db.session.commit()
        logger.info(f"Updated calendar: {calendar}")
        handle_calendar_delete(info, delete_calendar=False)
    except AttributeError:  # no matching record found
        logger.warning(f"No such entry in {Calendar.__tablename__} table with PK {primary_key}")


def handle_calendar_delete(info, delete_calendar=True):
    try:
        primary_key = (info['id'], info['user_id'])
        global_preferences = GlobalPreference.query.get(info['user_id'])
        calendar = Calendar.query.get(primary_key)
        all_overviews = get_all_sorted(info['user_id'])
        flag = False
        to_be_updated = []
        for overview in all_overviews:
            if overview.calendar_id == info['id'] and overview.user_id == info['user_id']:
                flag = True
                if not delete_calendar:  # calendar is not being deleted, we need to update this instruction
                    to_be_updated.append(overview)
            else:
                if flag:
                    to_be_updated.append(overview)
                flag = False
        if delete_calendar:
            db.session.delete(calendar)
            db.session.commit()
            logger.info(f"Deleted calendar with key {primary_key}")
        for overview in to_be_updated:
            calendar = Calendar.query.get((overview.calendar_id, overview.user_id))
            update_event_instructions(global_preferences, calendar, overview)
    except UnmappedError:  # no matching record found
        logger.warning(f"No such entry in {Calendar.__tablename__} table with PK {primary_key}")


def handle_preferences_create(info):
    info = {**{'user_id': info['user_id']}, **info['preferences']}
    preference = GlobalPreference(**info)
    db.session.add(preference)
    db.session.commit()
    logger.info(f"Created global preference with key: {info['user_id']}")


def handle_preferences_modify(info):
    try:
        primary_key = info['user_id']
        preference = GlobalPreference.query.get(primary_key)
        for k, v in info['preferences'].items():
            setattr(preference, k, v)
        db.session.commit()
        logger.info(f"Updated global preferences with key: {primary_key}")
        calendars = Calendar.query.filter_by(user_id=info['user_id']).all()
        for calendar in calendars:
            handle_calendar_delete({**info, **{'id': calendar.id}}, delete_calendar=False)
        modify_global_preferences(preference)
    except AttributeError as e:  # no matching record found
        logger.info(e)
        logger.warning(f"No such entry in {GlobalPreference.__tablename__} table with PK {primary_key}")


def handle_preferences_delete(info):
    try:
        primary_key = info['id']
        preference = GlobalPreference.query.get(primary_key)
        db.session.delete(preference)
        db.session.commit()
        logger.info(f"Deleted global preference with key {primary_key}")
    except UnmappedError:  # no matching record found
        logger.warning(f"No such entry in {GlobalPreference.__tablename__} table with PK {primary_key}")


def modify_global_preferences(global_preferences):
    global_preferences_to_update = db.session.query(GlobalPreference).filter(
        GlobalPreference.user_id == global_preferences.user_id).first()

    global_preferences_to_update.vehicles = global_preferences.vehicles
    global_preferences_to_update.personal_vehicles = global_preferences.personal_vehicles

    calendars = db.session.query(Calendar).filter(Calendar.user_id == global_preferences.user_id).all()

    gp = global_preferences
    for calendar in calendars:
        calendar.preferences = make_calendar_preferences_consistent(gp, calendar.preferences)
        flag_modified(calendar, "preferences")


def make_calendar_preferences_consistent(global_preferences, preferences):
    new_preferences = preferences

    for vehicle in new_preferences[:]:
        if not (vehicle['name'] in global_preferences.vehicles or
                vehicle['name'] in [p_vehicle['name'] for p_vehicle in global_preferences.personal_vehicles]):
            new_preferences.remove(vehicle)


    return new_preferences
