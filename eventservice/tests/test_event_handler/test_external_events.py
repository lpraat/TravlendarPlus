import json
import uuid

import pika

from src.configs import RABBITMQ_IP, RABBITMQ_PORT
from src.constants import CALENDAR_EXCHANGE, CALENDAR_CREATED_EVENT, CALENDAR_CREATED, CALENDAR_DELETED_EVENT, \
    CALENDAR_DELETED, PREFERENCES_DELETED_EVENT, PREFERENCES_DELETED
from src.eventhandler import create_connection
from src.queryrepository.data.event import CalendarId
from src.utils import session_scope
from tests.test_app import TestApp


class TestExternalEvents(TestApp):
    def setUp(self):
        super().setUp()

        def create_simulate_external_send():
            """
            To mock an external calendar micro service sending messages.
            :return:
            """
            connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
            channel = connection.channel()

            channel.exchange_declare(exchange=CALENDAR_EXCHANGE, exchange_type='topic')

            channel.confirm_delivery()

            return channel

        def publish_event(event, routing_key, channel=create_simulate_external_send()):
            return channel.basic_publish(exchange=CALENDAR_EXCHANGE,
                                         routing_key=routing_key,
                                         mandatory=True,
                                         properties=pika.BasicProperties(delivery_mode=2),
                                         body=event)

        # the function binded is used for publishing on the mocked sender
        self.publish_from_external = publish_event

    def test_external_events(self):
        calendar_created_event = dict(
            uuid=str(uuid.uuid4()),
            type=CALENDAR_CREATED_EVENT,
            event_info = dict(
                user_id=1, id=1, name='Home', description='', base=[35.1324, 36.1234],
                color=[243, 250, 152],
                active=True, carbon=True,
                preferences=dict(bus=dict(
                    time=None,
                    mileage=10
                ))
            )
        )
        self.publish_from_external(json.dumps(calendar_created_event), CALENDAR_CREATED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNotNone(session.query(CalendarId).filter(CalendarId.user_id == 1, CalendarId.id == 1).first())

        calendar_deleted_event = dict(
            uuid=str(uuid.uuid4()),
            type=CALENDAR_DELETED_EVENT,
            event_info=dict(
                user_id=1,
                id=1
            )
        )
        self.publish_from_external(json.dumps(calendar_deleted_event), CALENDAR_DELETED)
        self.simulate_eventual_consistency()
        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(CalendarId).filter(CalendarId.user_id == 1, CalendarId.id == 1).first())

        preferences_deleted_event = dict(
            uuid=str(uuid.uuid4()),
            type=PREFERENCES_DELETED_EVENT,
            event_info=dict(
                user_id=1
            )
        )

        calendar_created_event = dict(
            uuid=str(uuid.uuid4()),
            type=CALENDAR_CREATED_EVENT,
            event_info=dict(
                user_id=1, id=1, name='Job', description='', base=[35.1324, 36.1234],
                color=[243, 250, 152],
                active=True, carbon=True,
                preferences=dict(bus=dict(
                    time=None,
                    mileage=10
                ))
            )
        )

        self.publish_from_external(json.dumps(calendar_created_event), CALENDAR_CREATED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNotNone(session.query(CalendarId).filter(CalendarId.user_id == 1, CalendarId.id == 1).first())

        self.publish_from_external(json.dumps(preferences_deleted_event), PREFERENCES_DELETED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(CalendarId).filter(CalendarId.user_id == 1, CalendarId.id == 1).first())








