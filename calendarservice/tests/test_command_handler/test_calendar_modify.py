import json
import uuid

from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent
from src.queryrepository.data.calendar import Calendar
from src.queryrepository.data.calendar import GlobalPreferences
from src.utils import session_scope
from tests.test_app import TestApp


class TestCalendarModify(TestApp):
    def test_calendar_modify(self):
        default_vehicles = ['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy',
                            'mobike']
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

        put_data = json.dumps(dict(name='Test', description='Test sweet Test', base=[50, 50],
                                   color=[243, 250, 152],
                                   active=True, carbon=True,
                                   preferences=[dict(
                                       name='bus',
                                       time=['19:00', '20:30'],
                                       mileage=10
                                   )]))
        response = self.client.put('/users/1/calendars/1', data=put_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(
                session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 1).first().name,
                'Test'
            )

        put_data = json.dumps(dict(name='Test', description='Test sweet Test', base=[50, 50],
                                   color=[243, 250, 152],
                                   active=True, carbon=True,
                                   preferences=[
                                       dict(
                                           name='bus',
                                           time=['19:00', '20:30'],
                                           mileage=10
                                       ),
                                       dict(
                                           name='tesla',
                                           time=['19:00', '20:30'],
                                           mileage=100
                                       )]
                                   ))
        response = self.client.put('/users/1/calendars/1', data=put_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # there is no tesla in global preferences

        response = self.client.put('/users/1/calendars/3', data=put_data, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(json.loads(response.data)['error'], 'invalid calendar')

