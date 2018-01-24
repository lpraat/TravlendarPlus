from src.constants import USER_MODIFIED, USER_DELETED
from src.eventhandler.event_send import publish_event
from src.events.events import UserCreatedEvent, UserModifiedEvent, UserDeletedEvent
from src.queryrepository.data.user import User
from src.utils import hash_pass, session_scope
from tests.test_app import TestApp


class TestEvents(TestApp):
    def test_messages(self):
        event = UserCreatedEvent(1, 'test@hotmail.it', hash_pass('test_password'), 'test_first_name', 'test_last_name')
        publish_event(self.app.sending_channel, event, 'user.created')
        event = UserModifiedEvent(1, 'test@io.com', hash_pass('test_password'), 'test_first_name', 'test_last_name')
        publish_event(self.app.sending_channel, event, USER_MODIFIED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(session.query(User).filter(User.id == 1).first().email, 'test@io.com')

        event = UserDeletedEvent(1)
        publish_event(self.app.sending_channel, event, USER_DELETED)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(User).filter(User.id == 1).first())
