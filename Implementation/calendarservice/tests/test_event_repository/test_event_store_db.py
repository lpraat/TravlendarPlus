import json
import uuid

from src.constants import PREFERENCES_CREATED_EVENT
from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent
from src.utils import session_scope
from tests.test_app import TestApp


class TestEventStoreDB(TestApp):
    def test_add_event(self):
        with session_scope(self.EventStoreSession) as session:
            event = GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, dict(
                vehicles=['bus'],
                personal_vehicles=[dict(
                    name='tesla',
                    type='car',
                    location=(44.700546, 8.035837),
                    active=True
                )]))

            j_event = event.toJSON()
            CalendarEvent.append_event(event)
            q = session.query(CalendarEvent).first()
            self.assertEqual(q.event, j_event)
            self.assertEqual(json.loads(q.event)['type'], PREFERENCES_CREATED_EVENT)
