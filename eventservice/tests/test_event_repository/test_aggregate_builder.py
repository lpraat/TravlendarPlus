import datetime
import uuid

from src.eventrepository.aggregate_builder import build_event_aggregate
from src.eventrepository.data.event import EventEvent
from src.events.events import CalendarIdCreatedEvent, CalendarIdDeletedEvent, EventCreatedEvent, EventModifiedEvent, \
    EventDeletedEvent
from src.utils import strftime
from tests.test_app import TestApp


class TestAggregateBuilder(TestApp):
    def test_aggregate_builder(self):
        event1 = CalendarIdCreatedEvent(uuid=str(uuid.uuid4()), user_id=1, id=1)
        event2 = CalendarIdCreatedEvent(uuid=str(uuid.uuid4()), user_id=1, id=2)

        now = datetime.datetime.now()
        event3 = EventCreatedEvent(
            user_id=1,
            calendar_id=1,
            id=1,
            name='Meeting',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            recurrence_rule='NORMAL',
            next_is_base=False,
            until=None,
            flex=None,
            flex_duration=None
        )

        now = datetime.datetime.now()
        event4 = EventCreatedEvent(
            user_id=1,
            calendar_id=1,
            id=2,
            name='Cena Natalizia',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            next_is_base=False,
            recurrence_rule='DAILY',
            until=strftime(now + datetime.timedelta(days=3)),
            flex=True,
            flex_duration=3600
        )

        now = datetime.datetime.now()
        event5 = EventModifiedEvent(
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

        now = datetime.datetime.now()
        event6 = EventCreatedEvent(
            user_id=1,
            calendar_id=2,
            id=1,
            name='For lab',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            recurrence_rule='NORMAL',
            next_is_base=False,
            until=None,
            flex=None,
            flex_duration=None
        )

        event7 = CalendarIdCreatedEvent(uuid=str(uuid.uuid4()), user_id=2, id=1)

        now = datetime.datetime.now()
        event8 = EventCreatedEvent(
            user_id=2,
            calendar_id=1,
            id=1,
            name='Cinema',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            recurrence_rule='NORMAL',
            next_is_base=False,
            until=None,
            flex=None,
            flex_duration=None
        )

        event9 = EventDeletedEvent(
            user_id=1,
            calendar_id=1,
            id=2
        )

        EventEvent.append_event(event1)
        EventEvent.append_event(event2)
        EventEvent.append_event(event3)
        EventEvent.append_event(event4)
        EventEvent.append_event(event5)
        EventEvent.append_event(event6)
        EventEvent.append_event(event7)
        EventEvent.append_event(event8)
        EventEvent.append_event(event9)
        aggregate_status = build_event_aggregate()

        self.assertEqual(len(aggregate_status['1']['calendars'].keys()), 2)
        self.assertEqual(aggregate_status['1']['calendars']['1']['events']['1']['name'], 'Lol finals')
        self.assertEqual(len(aggregate_status['1']['calendars']['1']['events']['1']['recurrences'].keys()), 11)
        self.assertEqual(aggregate_status['2']['calendars']['1']['events']['1']['name'], 'Cinema')
        self.assertTrue('2' not in aggregate_status['1']['calendars']['1']['events'])

        event10 = CalendarIdDeletedEvent(uuid=str(uuid.uuid4()), user_id=1, id=1)

        EventEvent.append_event(event10)
        aggregate_status = build_event_aggregate()

        self.assertEqual(len(aggregate_status['1']['calendars'].keys()), 1)


