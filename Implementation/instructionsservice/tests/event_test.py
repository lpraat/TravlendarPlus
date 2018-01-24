import datetime
import json
import logging
import time
import unittest

from flask_testing import TestCase

from handler import create_connection, RABBITMQ_IP, RABBITMQ_PORT, CALENDAR_EXCHANGE, CALENDAR_CREATED, \
    publish_event, CALENDAR_DELETED, CALENDAR_MODIFIED, CALENDAR_CREATED_EVENT, CALENDAR_MODIFIED_EVENT, \
    CALENDAR_DELETED_EVENT, PREFERENCES_CREATED_EVENT, PREFERENCES_CREATED, PREFERENCES_MODIFIED_EVENT, \
    PREFERENCES_MODIFIED, PREFERENCES_DELETED_EVENT, PREFERENCES_DELETED, EVENT_CREATED_EVENT, EVENT_EXCHANGE, \
    EVENT_CREATED, EVENT_DELETED_EVENT, EVENT_DELETED, EVENT_MODIFIED_EVENT, EVENT_MODIFIED
from models import Calendar, GlobalPreference, Overview, Step
from src import db, create_app, setup_logging

DATE_START = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=12)  # approx tomorrow's noon

NORMALWAIT = 1
LONGWAIT = 3
COORDINATE_LAMBRATE = [45.4843, 9.2368]
COORDINATE_CADORNA = [45.4683, 9.1762]
COORDINATE_CENTRALE = [45.4865, 9.2031]
COORDINATE_UNREACHABLE = [20, 20]
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
# list containing all of tomorrow's hours
HOURS = [
    (datetime.datetime.now().replace(hour=x, minute=0, second=0) + datetime.timedelta(days=1)).strftime(DATE_FORMAT)
    for x in range(24)]


class AppTest(TestCase):
    RECURRENCES = 2
    test_calendar = {
        'name': 'Job', 'description': 'Job sweet job', 'base': COORDINATE_LAMBRATE, 'color': [243, 250, 152],
        'active': True, 'carbon': True, 'preferences': [{'mileage': None, 'name': 'bus', 'time': None},
                                                        {'mileage': None, 'name': 'subway', 'time': None},
                                                        {'mileage': None, 'name': 'train', 'time': None},
                                                        {'mileage': None, 'name': 'tram', 'time': None}]
    }
    test_preference = {
        'vehicles': ['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike'],
        'personal_vehicles': []}
    test_event = {
        'name': 'Pranzo Dalla Nonna',
        'location': COORDINATE_CADORNA,
        'start_time': HOURS[12],
        'end_time': HOURS[15],
        'recurrence_rule': 'DAILY',
        'until': (DATE_START + datetime.timedelta(days=RECURRENCES - 1)).strftime(DATE_FORMAT),
        'flex': None,
        'flex_duration': 100,
        'next_is_base': True
    }
    another_event = {'user_id': 1, 'calendar_id': 1, 'id': 1, 'name': 'Prova', 'location': [45.4839, 9.2513],
                     'start_time': '2018-01-07 13:00:00', 'end_time': '2018-01-07 14:00:00',
                     'recurrence_rule': 'NORMAL',
                     'next_is_base': False, 'until': None, 'flex': False, 'flex_duration': None}

    def create_app(self):
        setup_logging(path='../../logging.json', tofile=False)
        app = create_app(config='test_config')
        self.logger = logging.getLogger(__name__)
        connection = create_connection(RABBITMQ_IP, RABBITMQ_PORT)
        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=CALENDAR_EXCHANGE, exchange_type='topic')
        self.channel.exchange_declare(exchange=EVENT_EXCHANGE, exchange_type='topic')
        self.channel.confirm_delivery()
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()
        self.logger.info("Performed setUp")

    def tearDown(self):
        db.session.close_all()
        db.drop_all()
        self.logger.info("Performed teardown")

    def publish_external(self, exchange, event, routing_key, longwait=False):
        publish_event(self.channel, exchange, event, routing_key)
        time.sleep(LONGWAIT if longwait else NORMALWAIT)  # Simulate eventual consistency

    def test_calendar_create(self, id=1, user_id=1):
        event = {'type': CALENDAR_CREATED_EVENT, 'event_info': {**self.test_calendar, **{'id': id, 'user_id': user_id}}}
        self.test_preferences_create(user_id=user_id)
        self.publish_external(CALENDAR_EXCHANGE, json.dumps(event), CALENDAR_CREATED)
        self.assertEqual(len(Calendar.query.all()), 1)  # A calendar should be created

    def test_calendar_modify(self, id=1, user_id=1):
        self.test_calendar_create(id=id, user_id=user_id)
        new_base = COORDINATE_CENTRALE
        event = {'type': CALENDAR_MODIFIED_EVENT, 'event_info': {**self.test_calendar, **{
            'id': id, 'user_id': user_id, 'base': new_base}}}
        self.publish_external(CALENDAR_EXCHANGE, json.dumps(event), CALENDAR_MODIFIED)
        self.assertEqual(new_base, Calendar.query.get((id, user_id)).base)  # calendar should be updated

    def test_calendar_delete(self, id=1, user_id=1):
        event = {
            'type': CALENDAR_DELETED_EVENT,
            'event_info': {'id': id, 'user_id': user_id}
        }
        self.test_event_create(calendar_id=id, user_id=user_id)  # creates a new event
        self.publish_external(CALENDAR_EXCHANGE, json.dumps(event), CALENDAR_DELETED)
        self.assertEqual(0, len(Calendar.query.all()))  # No calendar should be present
        self.assertFalse(Overview.query.all())
        self.assertFalse(Step.query.all())

    def test_preferences_create(self, user_id=1):
        event = {
            'type': PREFERENCES_CREATED_EVENT,
            'event_info': {'preferences': self.test_preference, 'user_id': user_id}
        }
        self.publish_external(CALENDAR_EXCHANGE, json.dumps(event), PREFERENCES_CREATED)
        self.assertEqual(1, len(GlobalPreference.query.all()))  # a global preference should be created

    def test_preferences_modify(self, user_id=1):
        event = {
            'type': PREFERENCES_MODIFIED_EVENT,
            'event_info': {'preferences' :self.test_preference, 'user_id': user_id}
        }
        event['event_info']['preferences']['vehicles'].append('tram')
        self.test_preferences_create(user_id=user_id)
        self.publish_external(CALENDAR_EXCHANGE, json.dumps(event), PREFERENCES_MODIFIED)
        self.assertIn('tram', GlobalPreference.query.first().vehicles)  # preference should be updated

    def test_preferences_delete(self, user_id=1):
        event = {
            'type': PREFERENCES_DELETED_EVENT,
            'event_info': {'id': user_id}
        }
        self.test_event_create(user_id=user_id)
        self.publish_external(CALENDAR_EXCHANGE, json.dumps(event), PREFERENCES_DELETED)
        self.assertEqual(0, len(GlobalPreference.query.all()))  # preference should be deleted
        self.assertEqual(0, len(Calendar.query.all()))  # calendar should be deleted
        self.assertFalse(Overview.query.all())  # instructions should be deleted
        self.assertFalse(Step.query.all())  # steps should be deleted

    def test_event_create(self, id=1, user_id=1, calendar_id=1, create_calendar=True, testing=True, **kwargs):
        event = {
            'type': EVENT_CREATED_EVENT,
            'event_info': {**self.test_event, **{'id': id, 'user_id': user_id, 'calendar_id': calendar_id}, **kwargs}
        }
        if create_calendar:
            self.test_calendar_create(user_id=user_id)
        self.publish_external(EVENT_EXCHANGE, json.dumps(event), EVENT_CREATED, longwait=True)
        if False:
            self.assertEqual(self.RECURRENCES, len(Overview.query.filter_by(departure=True).all()))
            self.assertTrue(Overview.query.filter_by(departure=False).first())  # a return instruction should be created
            self.assertNotEqual(0, len(Step.query.all()))  # Corresponding steps should be created as well

    def test_fix_next_event(self):
        self.test_event_create(recurrence_rule='NORMAL', testing=False)
        # next I add a new event five hours ahead of this one with a new location
        new_start_time = HOURS[17]
        self.test_event_create(recurrence_rule="NORMAL", start_time=new_start_time, end_time=HOURS[20],
                               location=COORDINATE_CENTRALE, testing=False, create_calendar=False, id=2, name='2')
        # since the new inserted event is the last one, instructions for going back home should be updated
        instruction = Overview.query.filter_by(departure=False).first()
        self.assertEqual(COORDINATE_CENTRALE, [instruction.start_lat, instruction.start_lng])
        # add an event two hours before the added one
        new_start_time = HOURS[8]
        new_end_time = HOURS[9]
        self.test_event_create(recurrence_rule="NORMAL", start_time=new_start_time, end_time=new_end_time,
                               location=COORDINATE_CENTRALE, testing=False, create_calendar=False, id=3, name='3')
        # the instructions for the very first event that we've inserted should be updated
        instruction = Overview.query.get((1, 1, 1, 1, True))
        self.assertEqual(COORDINATE_CENTRALE, [instruction.start_lat, instruction.start_lng])
        # inserting an event that is unreachable affects other instruction as welL
        new_start_time = HOURS[10]
        new_end_time = HOURS[11]
        self.test_event_create(testing=False, create_calendar=False, id=4, name='4', location=COORDINATE_UNREACHABLE,
                               recurrence_rule="NORMAL", start_time=new_start_time, end_time=new_end_time)
        self.assertFalse(Overview.query.get((1, 1, 1, 4, True)).reachable)  # event inserted is not reachable
        self.assertFalse(Step.query.filter_by(event_id=4).all())  # no step should be created for that event
        # the instructions for the very first event that we've inserted should be unreachable as well
        db.session.refresh(instruction)
        self.assertFalse(Overview.query.get((1, 1, 1, 1, True)).reachable)

    def test_event_modify(self):
        self.test_event_create()
        event = {
            'type': EVENT_MODIFIED_EVENT,
            'event_info': {**self.test_event,
                           **{'location': COORDINATE_LAMBRATE, 'id': 1, 'user_id': 1, 'calendar_id': 1}}
        }
        self.publish_external(EVENT_EXCHANGE, json.dumps(event), EVENT_MODIFIED, longwait=True)
        x = Overview.query.get((1, 1, 1, 1, True))
        # event should be modified
        self.assertEqual(COORDINATE_LAMBRATE, [x.end_lat, x.end_lng])

    def test_event_delete(self):
        self.test_event_create()
        self.test_event_create(id=2, create_calendar=False, testing=False, start_time=HOURS[10], end_time=HOURS[11],
                               recurrence_rule="NORMAL", location=COORDINATE_CENTRALE)
        self.test_event_create(id=3, create_calendar=False, testing=False, start_time=HOURS[14], end_time=HOURS[15],
                               recurrence_rule="NORMAL", location=COORDINATE_CENTRALE)
        event = {
            'type': EVENT_DELETED_EVENT,
            'event_info': {'id': 2, 'user_id': 1, 'calendar_id': 1, 'next_is_base': True}
        }
        self.publish_external(EVENT_EXCHANGE, json.dumps(event), EVENT_DELETED)
        # deleting event #2 should update event #1, shifting the departure to calendar base location
        x = Overview.query.get((1, 1, 1, 1, True))
        self.assertEqual(COORDINATE_LAMBRATE, [x.start_lat, x.start_lng])
        event['event_info']['id'] = 3
        self.publish_external(EVENT_EXCHANGE, json.dumps(event), EVENT_DELETED)
        # deleting event #3 should update return instruction, shifting the departure to event #1 location
        x = Overview.query.get((1, 1, 1, 1, False))
        self.assertEqual(COORDINATE_CADORNA, [x.start_lat, x.start_lng])
        event['event_info']['id'] = 1
        self.publish_external(EVENT_EXCHANGE, json.dumps(event), EVENT_DELETED)
        # deleting the only event remaining should remove everything from the database, return instruction included
        self.assertFalse(Overview.query.all())  # all overviews should be deleted
        self.assertFalse(Step.query.all())  # all steps should be deleted accordingly

    def test_base_return(self):
        self.test_event_create(testing=False, next_is_base=False)
        self.assertFalse(Overview.query.filter_by(departure=False).all())  # no return instruction

    def test_get_endpoint(self):
        self.test_event_create()
        response = self.client.get('/users/1/calendars/1/events/1/recurrence/1/instruction').json
        self.logger.info(response)
    #
    # def test_error(self):
    #     self.test_event_create(next_is_base=False, recurrence_rule="NORMAL")
    #     self.test_event_create(id=2, create_calendar=False, testing=False, start_time=HOURS[18], end_time=HOURS[20],
    #                            recurrence_rule="NORMAL", location=COORDINATE_CENTRALE, next_is_base=False)
    #     self.test_event_create(id=3, create_calendar=False, testing=False, start_time=HOURS[16], end_time=HOURS[17],
    #                            recurrence_rule="NORMAL", location=COORDINATE_CENTRALE, flex_duration=100, next_is_base=False)


if __name__ == '__main__':
    unittest.main()
