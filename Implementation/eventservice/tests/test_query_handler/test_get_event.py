import datetime
import json
import uuid

from src.eventrepository.data.event import EventEvent
from src.events.events import CalendarIdCreatedEvent
from src.queryrepository.data.event import CalendarId
from src.utils import session_scope, strftime
from tests.test_app import TestApp


class TestGetEvent(TestApp):
    def test_event_get(self):
        event = CalendarIdCreatedEvent(str(uuid.uuid4()), 1, 1)
        EventEvent.append_event(event)

        with session_scope(self.DBSession) as session:
            session.add(CalendarId(
                user_id=1,
                id=1))

        now = datetime.datetime.now()
        post_data = json.dumps(
            dict(name='Evento',
                 location=[44.6368, 10.5697],
                 start_time=strftime((now + datetime.timedelta(days=1))),
                 end_time=strftime((now + datetime.timedelta(days=1, hours=1))),
                 recurrence_rule='MONTHLY',
                 next_is_base=False,
                 until=strftime(datetime.datetime(year=2018, month=2, day=1)),
                 flex=True,
                 flex_duration=1800))

        self.client.post('/users/1/calendars/1/events', data=post_data, content_type='application/json')
        self.simulate_eventual_consistency()

        response = self.client.get('/users/1/calendars/1/events/1')
        self.assertEqual(response.status_code, 200)
