import json
import uuid

from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent
from src.queryrepository.data.calendar import GlobalPreferences
from src.utils import session_scope
from tests.test_app import TestApp


class TestGetCalendar(TestApp):
    def test_calendar_get(self):
        default_vehicles = ['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']
        default_preferences = dict(vehicles=default_vehicles, personal_vehicles=dict())

        with session_scope(self.DBSession) as session:
            session.add(GlobalPreferences(
                user_id=1,
                preferences=default_preferences))

        CalendarEvent.append_event(GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, default_preferences))

        response = self.client.get('/users/4/preferences')
        self.assertEqual(response.status_code, 404)

        response = self.client.get('/users/1/preferences')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['vehicles'], default_vehicles)


