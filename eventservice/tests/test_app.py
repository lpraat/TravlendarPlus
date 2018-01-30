import time
import unittest
from threading import Thread

from src import create_app
from src import register_blueprints
from src.configs import RABBITMQ_IP, RABBITMQ_PORT
from src.eventhandler import create_connection, setup_channel_for_sending, setup_channel_for_receiving
from src.eventhandler.event_receive import receive
from src.eventrepository import event_store_engine, EventStoreSession
from src.eventrepository.data.event import EventStoreBase
from src.queryrepository import db_engine, DBSession
from src.queryrepository.data.event import DBBase


class TestApp(unittest.TestCase):
    """
    Setup for unit and integration tests.
    To run this tests the event store, the database and message broker have to be up and running.
    """
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        register_blueprints(self.app)

        self.DBBase = DBBase
        self.EventStoreBase = EventStoreBase
        self.DBSession = DBSession
        self.EventStoreSession = EventStoreSession

        # to mock a client doing REST API calls
        self.client = self.app.test_client()

        # to simulate eventual consistency between the command and the query side
        self.simulate_eventual_consistency = lambda: time.sleep(0.1)

        DBBase.metadata.create_all(db_engine)
        EventStoreBase.metadata.create_all(event_store_engine)

        self.conn = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
        self.app.sending_channel = setup_channel_for_sending()
        self.app.secret_key = '\x0c|f9\x91%1\xb2\xd2\xdd\xeeM\x15\xa1\xf1\xb09U\xb5Oj&\xe0M'
        self.t = Thread(target=receive, args=(setup_channel_for_receiving(),))
        self.t.daemon = True
        self.t.start()

    def tearDown(self):
        self.DBBase.metadata.drop_all(db_engine)
        self.EventStoreBase.metadata.drop_all(event_store_engine)
        self.conn.close()
