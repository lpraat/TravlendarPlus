import json

from src.eventrepository.aggregate_builder import build_user_aggregate
from src.eventrepository.data.event import UserEvent
from src.events.events import UserCreatedEvent, UserModifiedEvent, UserDeletedEvent
from src.utils import hash_pass
from tests.test_app import TestApp


class TestAggregateBuilder(TestApp):

    def test_build_aggregate(self):
        event1 = UserCreatedEvent(1, 'test1@hotmail.it', hash_pass('test1_password'), 'test_first_name',
                                  'test_last_name')
        event2 = UserModifiedEvent(1, 'test2@hotmail.it', hash_pass('test2_password'), 'test_first_name',
                                   'test_last_name')
        event3 = UserCreatedEvent(2, 'prova@hotmail.it', hash_pass('test1_password'), 'prova_first_name',
                                  'prova_last_name')
        event4 = UserDeletedEvent(1)

        UserEvent.append_event(event1)
        UserEvent.append_event(event2)
        UserEvent.append_event(event3)
        UserEvent.append_event(event4)

        aggregate_status = build_user_aggregate()
        expected_status = {}
        event3 = json.loads(event3.toJSON())
        expected_status[str(event3['event_info']['id'])] = event3['event_info']
        self.assertEqual(aggregate_status, expected_status)

