import uuid

from src.constants import PREFERENCES_CREATED, PREFERENCES_MODIFIED, PREFERENCES_DELETED, CALENDAR_CREATED, \
    CALENDAR_MODIFIED, CALENDAR_DELETED
from src.eventhandler.event_send import publish_event
from src.events.events import GlobalPreferencesCreatedEvent, GlobalPreferencesModifiedEvent, \
    GlobalPreferencesDeletedEvent, CalendarCreatedEvent, CalendarModifiedEvent, CalendarDeletedEvent
from src.queryrepository.data.calendar import Calendar
from src.queryrepository.data.calendar import GlobalPreferences
from src.utils import session_scope
from tests.test_app import TestApp


class TestEvents(TestApp):
    def test_messages(self):
        # Global Preferences
        event = GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, dict(
            vehicles=['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']))
        publish_event(self.app.sending_channel, event, PREFERENCES_CREATED)
        self.simulate_eventual_consistency()

        event = GlobalPreferencesModifiedEvent(1, dict(vehicles=['mobike']))
        publish_event(self.app.sending_channel, event, PREFERENCES_MODIFIED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(
                session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 1).first().preferences['vehicles'],
                ['mobike']
            )

        event = GlobalPreferencesDeletedEvent(str(uuid.uuid4()), 1)
        publish_event(self.app.sending_channel, event, PREFERENCES_DELETED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 1).first())

        # Calendar
        event = GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, dict(
            vehicles=['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']))
        publish_event(self.app.sending_channel, event, PREFERENCES_CREATED)
        self.simulate_eventual_consistency()

        event = CalendarCreatedEvent(user_id=1, id=1, name='Home', description='', base=[35.1324, 36.1234],
                                     color=[243, 250, 152], active=True, carbon=True,
                                     preferences=[dict(
                                         name='bus',
                                         time=None,
                                         mileage=10
                                     )])
        publish_event(self.app.sending_channel, event, CALENDAR_CREATED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(
                session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 1).first().name,
                'Home'
            )

        event = CalendarModifiedEvent(user_id=1, id=1, name='Home', description='Home sweet home', base=[50, 50],
                                      color=[243, 250, 152], active=True, carbon=True,
                                      preferences=[dict(
                                          name='bus',
                                          time=None,
                                          mileage=10
                                      )])
        publish_event(self.app.sending_channel, event, CALENDAR_MODIFIED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(
                session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 1).first().description,
                'Home sweet home'
            )
            self.assertEqual(
                session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 1).first().base,
                [50, 50]
            )

        event = CalendarDeletedEvent(user_id=1, id=1)
        publish_event(self.app.sending_channel, event, CALENDAR_DELETED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(Calendar).filter(Calendar.user_id == 1, Calendar.id == 1).first())

    def test_gp_modify(self):
        event = GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, dict(
            vehicles=['bus', 'subway', 'train', 'tram', 'car', 'walking', 'bike', 'taxi', 'enjoy', 'mobike']))
        publish_event(self.app.sending_channel, event, PREFERENCES_CREATED)
        self.simulate_eventual_consistency()

        event = CalendarCreatedEvent(user_id=1, id=1, name='Home', description='', base=[35.1324, 36.1234],
                                     color=[243, 250, 152], active=True, carbon=True,
                                     preferences=[dict(
                                         name='bus',
                                         time=None,
                                         mileage=10
                                     )])
        publish_event(self.app.sending_channel, event, CALENDAR_CREATED)
        self.simulate_eventual_consistency()

        event = GlobalPreferencesModifiedEvent(1, dict(vehicles=['mobike']))
        publish_event(self.app.sending_channel, event, PREFERENCES_MODIFIED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(session.query(Calendar).filter(Calendar.user_id == 1,
                                                                      Calendar.id == 1).first().preferences, [])
