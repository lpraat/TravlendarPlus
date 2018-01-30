import datetime
import json
import uuid

from src.eventrepository.data.event import EventEvent
from src.events.events import CalendarIdCreatedEvent
from src.queryrepository.data.event import CalendarId
from src.utils import session_scope, strftime
from tests.test_app import TestApp


class TestGetSchedule(TestApp):
    def test_schedule_get(self):
        event = CalendarIdCreatedEvent(str(uuid.uuid4()), 1, 1)
        EventEvent.append_event(event)

        with session_scope(self.DBSession) as session:
            session.add(CalendarId(
                user_id=1,
                id=1))

        now = datetime.datetime.now()

        for i in range(0, 3):
            post_data = json.dumps(
                dict(name=f'Evento {i}',
                     location=[44.6368, 10.5697],
                     start_time=strftime((now + datetime.timedelta(days=i))),
                     end_time=strftime((now + datetime.timedelta(days=i, hours=1))),
                     recurrence_rule='MONTHLY',
                     next_is_base=False,
                     until=strftime(datetime.datetime(year=2018, month=2, day=1)),
                     flex=True,
                     flex_duration=1800))

            self.client.post('/users/1/calendars/1/events', data=post_data, content_type='application/json')
            self.simulate_eventual_consistency()

        response = self.client.get('/users/1/schedule')
        self.assertEqual(len(json.loads(response.data)), 1)