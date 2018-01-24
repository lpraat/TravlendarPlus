import json
import uuid

from src.constants import CALENDAR_ID_CREATED_EVENT
from src.eventrepository.data.event import EventEvent
from src.events.events import CalendarIdCreatedEvent
from src.utils import session_scope
from tests.test_app import TestApp


class TestEventStoreDB(TestApp):

    def test_add_event(self):
        with session_scope(self.EventStoreSession) as session:
            event = CalendarIdCreatedEvent(str(uuid.uuid4()), 1, 1)
            j_event = event.toJSON()
            EventEvent.append_event(event)
            q = session.query(EventEvent).first()
            self.assertEqual(q.event, j_event)
            self.assertEqual(json.loads(q.event)['type'], CALENDAR_ID_CREATED_EVENT)
