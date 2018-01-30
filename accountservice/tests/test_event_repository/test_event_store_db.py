import json

from src.constants import USER_CREATED_EVENT
from src.eventrepository.data.event import UserEvent
from src.events.events import UserCreatedEvent
from src.utils import hash_pass, session_scope
from tests.test_app import TestApp


class TestEventStoreDB(TestApp):
    def test_add_event(self):
        with session_scope(self.EventStoreSession) as session:
            event = UserCreatedEvent(1, 'test@hotmail.it', hash_pass('test_password'), 'test_first_name',
                                     'test_last_name')
            j_event = event.toJSON()
            session.add(UserEvent(uuid=event.uuid, event=j_event))
            q = session.query(UserEvent).first()
            self.assertEqual(q.event, j_event)
            self.assertEqual(json.loads(q.event)['type'], USER_CREATED_EVENT)
