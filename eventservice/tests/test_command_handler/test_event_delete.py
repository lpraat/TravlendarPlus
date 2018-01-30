import datetime
import json
import uuid

from src.eventrepository.data.event import EventEvent
from src.events.events import CalendarIdCreatedEvent
from src.queryrepository.data.event import CalendarId
from src.queryrepository.data.event import Event
from src.utils import session_scope, strftime
from tests.test_app import TestApp


class TestEventDelete(TestApp):

    def test_event_delete(self):
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

        self.client.post('/users/1/calendars/1/events', data=post_data, content_type='application/json')
        self.simulate_eventual_consistency()

        self.client.delete('/users/1/calendars/1/events/1')
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(Event).first())
