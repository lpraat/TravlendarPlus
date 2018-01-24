import json
import uuid

import pika

from src.configs import RABBITMQ_IP, RABBITMQ_PORT
from src.constants import ACCOUNT_EXCHANGE, USER_CREATED_EVENT, USER_CREATED, USER_DELETED_EVENT, USER_DELETED
from src.eventhandler import create_connection
from src.queryrepository.data.calendar import GlobalPreferences
from src.utils import session_scope
from tests.test_app import TestApp


class TestExternalEvents(TestApp):
    def setUp(self):
        super().setUp()

        def create_simulate_external_send():
            """
            To mock an external account micro service sending messages.
            :return:
            """
            connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
            channel = connection.channel()

            channel.exchange_declare(exchange=ACCOUNT_EXCHANGE, exchange_type='topic')

            channel.confirm_delivery()

            return channel

        def publish_event(event, routing_key, channel=create_simulate_external_send()):
            return channel.basic_publish(exchange=ACCOUNT_EXCHANGE,
                                         routing_key=routing_key,
                                         mandatory=True,
                                         properties=pika.BasicProperties(delivery_mode=2),
                                         body=event)

        # the function binded is used for publishing on the mocked sender
        self.publish_from_external = publish_event

    def test_external_events(self):
        user_created_event = dict(
            uuid=str(uuid.uuid4()),
            type=USER_CREATED_EVENT,
            event_info=dict(
                id='234',
                email='prova@prova.it',
                password='$2b$12$VqFmp6M/ANsKPUV7.1a4yOCMy0ITf6lgVTc/IkuS6zdCXbX6o.TA.',
                first_name='prova',
                last_name='prova'
            )
        )
        self.publish_from_external(json.dumps(user_created_event), USER_CREATED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNotNone(session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 234).first())

        user_deleted_event = dict(
            uuid=str(uuid.uuid4()),
            type=USER_DELETED_EVENT,
            event_info=dict(
                id='234'
            )
        )
        self.publish_from_external(json.dumps(user_deleted_event), USER_DELETED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 234).first())
