import uuid

from src.eventrepository.aggregate_builder import build_calendar_aggregate
from src.eventrepository.data.event import CalendarEvent
from src.events.events import GlobalPreferencesCreatedEvent, CalendarCreatedEvent, CalendarModifiedEvent, \
    CalendarDeletedEvent, GlobalPreferencesModifiedEvent
from tests.test_app import TestApp


class TestAggregateBuilder(TestApp):
    def test_build_aggregate(self):
        event1 = GlobalPreferencesCreatedEvent(str(uuid.uuid4()), 1, dict(
            vehicles=['bus'],
            personal_vehicles=[dict(
                name='tesla',
                type='car',
                location=(44.700546, 8.035837),
                active=True
            )]))

        event2 = CalendarCreatedEvent(user_id=1, id=1, name='Home', description='Home sweet home', base=[50, 50],
                                      color=[243, 250, 152], active=True, carbon=True,
                                      preferences=[dict(
                                          name='bus',
                                          time=['19:00', '20:30'],
                                          mileage=5)])

        event3 = CalendarCreatedEvent(user_id=1, id=2, name='Job', description='Job sweet job', base=[20, 20],
                                      color=[243, 250, 152], active=True, carbon=True,
                                      preferences=[dict(
                                          name='bus',
                                          time=['19:00', '20:30'],
                                          mileage=5)])

        event4 = CalendarModifiedEvent(user_id=1, id=1, name='Home', description='Home not so sweet home',
                                       base=[50, 50], color=[243, 250, 152], active=True, carbon=True,
                                       preferences=[
                                           dict(
                                               name='bus',
                                               time=['19:00', '20:30'],
                                               mileage=5),
                                           dict(
                                               name='tesla',
                                               time=['19:00', '20:30'],
                                               mileage=200
                                           )])

        event5 = CalendarDeletedEvent(user_id=1, id=2)

        event6 = GlobalPreferencesModifiedEvent(1, dict(
            personal_vehicles=[dict(
                    name='tesla',
                    type='car',
                    location=(44.700546, 8.035837),
                    active=True
                )]))

        CalendarEvent.append_event(event1)
        CalendarEvent.append_event(event2)
        CalendarEvent.append_event(event3)
        CalendarEvent.append_event(event4)
        CalendarEvent.append_event(event5)
        CalendarEvent.append_event(event6)

        aggregate_status = build_calendar_aggregate()

        self.assertEqual(aggregate_status['1']['calendars']['1']['description'], 'Home not so sweet home')
        self.assertFalse('2' in aggregate_status['1']['calendars'])
        self.assertTrue('bus' not in [vehicle['name'] for vehicle in aggregate_status['1']['calendars']['1']['preferences']])
