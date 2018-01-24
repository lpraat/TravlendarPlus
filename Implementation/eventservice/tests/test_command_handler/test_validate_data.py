import datetime

from src.commandhandler.validate_data import validate_event
from src.utils import strftime
from tests.test_app import TestApp


class TestValidations(TestApp):

    def test_event_validations(self):
        now = datetime.datetime.now()
        event_from_client = dict(
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now+datetime.timedelta(hours=1)),
            recurrence_rule='NORMAL',
            next_is_base=False
        )
        self.assertTrue(validate_event(event_from_client))

        event_from_client = dict(
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now - datetime.timedelta(hours=1)),
            recurrence_rule='NORMAL',
            next_is_base=False
        )
        self.assertFalse(validate_event(event_from_client))

        event_from_client = dict(
            name='Pranzo Dalla Nonna',
            location=[204.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            recurrence_rule='NORMAL',
            next_is_base=False
        )
        self.assertFalse(validate_event(event_from_client))

        event_from_client = dict(
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            recurrence_rule='DAILY',
            next_is_base=False,
            until=strftime(now + datetime.timedelta(days=3)),
            flex=None,
            flex_duration=None

        )
        self.assertTrue(validate_event(event_from_client))

        event_from_client = dict(
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(days=2)),
            recurrence_rule='DAILY',
            next_is_base=False,
            until=strftime(now + datetime.timedelta(days=3)),
            flex=None,
            flex_duration=None
        )
        self.assertFalse(validate_event(event_from_client))

        event_from_client = dict(
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            recurrence_rule='DAILY',
            next_is_base=False,
            until=strftime(now + datetime.timedelta(days=3)),
            flex=True,
            flex_duration=1800
        )
        self.assertTrue(validate_event(event_from_client))

        event_from_client = dict(
            name='Pranzo Dalla Nonna',
            location=[44.6368, 10.5697],
            start_time=strftime(now),
            end_time=strftime(now + datetime.timedelta(hours=1)),
            recurrence_rule='DAILY',
            next_is_base=False,
            until=strftime(now + datetime.timedelta(days=3)),
            flex=True,
            flex_duration=3600
        )
        self.assertFalse(validate_event(event_from_client))

