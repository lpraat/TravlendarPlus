import datetime
import unittest

from flask_testing import TestCase

from instructions import yield_recurrences
from src import db, create_app, setup_logging


class AppTest(TestCase):
    data = {'origin': '45.4842721,9.2368349',  # Piazza Enrico Bottini
            'destination': '45.468359,9.1761419',  # Cadorna
            'mode': 'transit'}

    test_global_preferences = {
        'vehicles': ['bus', 'tram', 'taxi'],
        'personal_vehicles': {
            'tesla': {'type': 'car', 'location': [20, 20], 'active': True},
            'bianchi': {'type': 'bike', 'location': [20, 20], 'active': True}
        }
    }
    test_calendar_preferences = {
        'bus': {'time': ['8:00', '15:00'], 'mileage': 500}
    }
    DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    test_event = {
        'name': 'Pranzo Dalla Nonna', 'location': [44.6368, 10.5697],
        'start_time': datetime.datetime.now().strftime(DATE_FORMAT),
        'end_time': (datetime.datetime.now() + datetime.timedelta(hours=1)).strftime(DATE_FORMAT),
        'recurrence_rule': 'DAILY',
        'until': (datetime.datetime.now() + datetime.timedelta(days=3)).strftime(DATE_FORMAT),
        'flex': None,
        'flex_duration': None
    }

    def create_app(self):
        setup_logging(path='../../logging.json', tofile=False)
        app = create_app(config='test_config')
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_yield_recurrences(self):
        # 4 recurrences should be created if until is set to 3 days in the future
        self.assertEqual(4, len(list(rec for rec in yield_recurrences(self.test_event))))
        self.assertEqual(1, len(list(rec for rec in yield_recurrences({**self.test_event, **{'recurrence_rule': 'NORMAL'}}))))


if __name__ == '__main__':
    unittest.main()
