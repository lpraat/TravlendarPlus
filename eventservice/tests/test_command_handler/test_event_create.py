import datetime
import json
import uuid

from src.eventrepository.data.event import EventEvent
from src.events.events import CalendarIdCreatedEvent
from src.queryrepository.data.event import CalendarId
from src.utils import session_scope, strftime
from tests.test_app import TestApp


class TestEventCreate(TestApp):
    def test_event_create(self):

        event = CalendarIdCreatedEvent(str(uuid.uuid4()), 1, 1)
        EventEvent.append_event(event)

        with session_scope(self.DBSession) as session:
            session.add(CalendarId(
                user_id=1,
                id=1))

        now = datetime.datetime.now()
        post_data = json.dumps(
            dict(name='Pranzo Dalla Nonna',
                 location=[44.6368, 10.5697],
                 start_time=strftime(now),
                 end_time=strftime(now + datetime.timedelta(hours=1)),
                 recurrence_rule='DAILY',
                 next_is_base=False,
                 until=strftime(now + datetime.timedelta(days=3)),
                 flex=True,
                 flex_duration=1800))

        response = self.client.post('/users/1/calendars/1/events', data=post_data, content_type='application/json')
        self.simulate_eventual_consistency()
        self.assertEqual(response.status_code, 201)

        now = datetime.datetime.now()
        post_data = json.dumps(
            dict(name='Football Match',
                 location=[44.6368, 10.5697],
                 start_time=strftime(now + datetime.timedelta(days=3)),
                 end_time=strftime(now + datetime.timedelta(days=4)),
                 recurrence_rule='NORMAL',
                 next_is_base=False,
                 until=None,
                 flex=None,
                 flex_duration=None))

        response = self.client.post('/users/1/calendars/1/events', data=post_data, content_type='application/json')
        self.simulate_eventual_consistency()
        self.assertEqual(response.status_code, 400)  # the event overlaps

        now = datetime.datetime.now()
        post_data = json.dumps(
            dict(name='Football Match',
                 location=[44.6368, 10.5697],
                 start_time=strftime(now + datetime.timedelta(days=10)),
                 end_time=strftime(now + datetime.timedelta(days=12)),
                 recurrence_rule='NORMAL',
                 next_is_base=False,
                 until=None,
                 flex=None,
                 flex_duration=None))

        response = self.client.post('/users/1/calendars/1/events', data=post_data, content_type='application/json')
        self.simulate_eventual_consistency()
        self.assertEqual(response.status_code, 201)

