import json
import uuid

from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent
from src.queryrepository.data.calendar import Calendar
from src.queryrepository.data.calendar import GlobalPreferences
from src.utils import session_scope
from tests.test_app import TestApp


class TestCalendarCreate(TestApp):
    def test_calendar_create(self):
        default_vehicles = ['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']
        default_preferences = dict(vehicles=default_vehicles, personal_vehicles=[])

        with session_scope(self.DBSession) as session:
            session.add(GlobalPreferences(
                user_id=1,
                preferences=default_preferences))

        CalendarEvent.append_event(GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, default_preferences))

        post_data = json.dumps(dict(name='Home', description='', base=[44.6381,10.5726],
                                    color=[243, 250, 0],
                                    active=False, carbon=False,
                                    preferences=[dict(
                                            name='bus',
                                            time=None,
                                            mileage=None
                                        )]))
        response = self.client.post('/users/1/calendars', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(
                session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 1).first().name,
                'Home'
            )

        post_data = json.dumps(dict(name='Job', description='Job sweet job', base=[50.20, 50],
                                    color=[243, 250, 152],
                                    active=True, carbon=True,
                                    preferences=[dict(
                                        name='bus',
                                        time=['19:00', '20:30'],
                                        mileage=10
                                    )]))
        response = self.client.post('/users/1/calendars', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data)['id'], 2)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 2).first().name,
                             'Job')

        post_data = json.dumps(dict(name='Home', description='second home', base=[50, 50],
                                    color=[243, 250, 152],
                                    active=True, carbon=True,
                                    preferences=[dict(
                                        name='bus',
                                        time=['19:00', '20:30'],
                                        mileage=10
                                    )]
                                    ))
        response = self.client.post('/users/1/calendars', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # name already present

        post_data = json.dumps(dict(name='Home', description='second home', base=[50, 50],
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
                                            time=None,
                                            mileage=None
                                        )
                                        ]
                                    ))
        response = self.client.post('/users/1/calendars', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # tesla not in global preferences
