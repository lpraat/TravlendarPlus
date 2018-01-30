import datetime
import uuid

from src.constants import CALENDAR_ID_CREATED, EVENT_CREATED, EVENT_MODIFIED, EVENT_DELETED, CALENDAR_ID_DELETED
from src.eventhandler.event_send import publish_event
from src.events.events import CalendarIdCreatedEvent, EventCreatedEvent, EventModifiedEvent, EventDeletedEvent, \
    CalendarIdDeletedEvent
from src.queryrepository.data.event import Event, Recurrence
from src.utils import session_scope, strftime
from tests.test_app import TestApp


class TestEvents(TestApp):
    def test_events(self):
        event = CalendarIdCreatedEvent(str(uuid.uuid4()), 1, 1)
        publish_event(self.app.sending_channel, event, CALENDAR_ID_CREATED)
        self.simulate_eventual_consistency()

        now = datetime.datetime.now()

        event = EventCreatedEvent(
            user_id=1,
            calendar_id=1,
            id=1,
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            next_is_base=False,
            recurrence_rule='DAILY',
            until=strftime(now + datetime.timedelta(days=3)),
            flex=True,
            flex_duration=3600
        )
        publish_event(self.app.sending_channel, event, EVENT_CREATED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(len(session.query(Recurrence).all()), 4)

        event = EventModifiedEvent(
            user_id=1,
            calendar_id=1,
            id=1,
            name='Lol finals',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            next_is_base=False,
            recurrence_rule='DAILY',
            until=strftime(now + datetime.timedelta(days=10)),
            flex=True,
            flex_duration=3600
        )
        publish_event(self.app.sending_channel, event, EVENT_MODIFIED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(len(session.query(Event).all()), 1)
            self.assertEqual(session.query(Event).first().name, 'Lol finals')
            self.assertEqual(len(session.query(Recurrence).all()), 11)

        event = EventDeletedEvent(
            user_id=1,
            calendar_id=1,
            id=1
        )
        publish_event(self.app.sending_channel, event, EVENT_DELETED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(Event).first())
            self.assertIsNone(session.query(Recurrence).first())

        event = EventCreatedEvent(
            user_id=1,
            calendar_id=1,
            id=1,
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            next_is_base=False,
            recurrence_rule='NORMAL',
            until=None,
            flex=None,
            flex_duration=None
        )
        publish_event(self.app.sending_channel, event, EVENT_CREATED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(len(session.query(Recurrence).all()), 1)

        event = CalendarIdDeletedEvent(str(uuid.uuid4()), 1, 1)
        publish_event(self.app.sending_channel, event, CALENDAR_ID_DELETED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(Event).first())
            self.assertIsNone(session.query(Recurrence).first())





