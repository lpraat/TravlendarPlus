import uuid

from flask import json

from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent
from src.queryrepository.data.calendar import GlobalPreferences
from src.utils import session_scope
from tests.test_app import TestApp


class TestGlobalPreferencesModify(TestApp):
    def test_global_preferences_modify(self):
        default_vehicles = ['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']
        default_preferences = dict(vehicles=default_vehicles, personal_vehicles=[])

        with session_scope(self.DBSession) as session:
            session.add(GlobalPreferences(
                user_id=1,
                preferences=default_preferences))

        CalendarEvent.append_event(GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, default_preferences))

        new_preferences = json.dumps(dict(
            vehicles=['bus', 'subway'],
            personal_vehicles=[
                dict(
                    name="tesla",
                    type='car',
                    location=(13, 14),
                    active=True
                )
            ])
        )
        response = self.client.put('/users/1/preferences', data=new_preferences, content_type='application/json')
        self.assertTrue(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['id'], 1)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(
                session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 1).first().preferences,
                json.loads(new_preferences))

        response = self.client.put('/users/10/preferences', data=new_preferences, content_type='application/json')
        self.assertTrue(response.status_code, 404)
