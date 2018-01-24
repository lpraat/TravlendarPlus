import json
import uuid

from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent
from src.queryrepository.data.calendar import Calendar
from src.queryrepository.data.calendar import GlobalPreferences
from src.utils import session_scope
from tests.test_app import TestApp


class TestCalendarDelete(TestApp):
    def test_calendar_delete(self):
        default_vehicles = ['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']
        default_preferences = dict(vehicles=default_vehicles, personal_vehicles=[])

        with session_scope(self.DBSession) as session:
            session.add(GlobalPreferences(
                user_id=1,
                preferences=default_preferences))

        CalendarEvent.append_event(GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, default_preferences))

        post_data = json.dumps(dict(name='Home', description='Home sweet home', base=[50, 50],
                                    color=[243, 250, 152],
                                    active=True, carbon=True,
                                    preferences=[dict(
                                        name='bus',
                                        time=['19:00', '20:30'],
                                        mileage=10
                                    )]))
        self.client.post('/users/1/calendars', data=post_data, content_type='application/json')
        self.simulate_eventual_consistency()

        self.client.delete('/users/1/calendars/1')
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 1).first())
