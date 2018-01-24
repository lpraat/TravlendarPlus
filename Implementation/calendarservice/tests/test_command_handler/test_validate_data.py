import json

from src.commandhandler.validate_data_calendar import validate_calendar_data, validate_calendar_preferences
from src.commandhandler.validate_data_preferences import validate_global_preferences
from tests.test_app import TestApp


class TestValidations(TestApp):
    def test_gp_validations(self):
        preferences_from_client = json.dumps(dict(
            vehicles=['bus'],
            personal_vehicles=[
                dict(
                    name='tesla',
                    type='car',
                    location=[44.700546, 8.035837],
                    active=True
                )
            ]
            ))
        self.assertTrue(validate_global_preferences(json.loads(preferences_from_client)))

        preferences_from_client = json.dumps(dict(
            vehicles=['plane']
        ))
        self.assertFalse(validate_global_preferences(json.loads(preferences_from_client)))

        preferences_from_client = json.dumps(dict(
            vehicles=['bus', 'car'],
            personal_vehicles=[
                dict(
                    name='tesla',
                    type='car',
                    location=180,
                    active=True
                )
            ])
        )
        self.assertFalse(validate_global_preferences(json.loads(preferences_from_client)))

        preferences_from_client = json.dumps(dict(
            personal_vehicles=[
                dict(
                    name='bmw',
                    type='car',
                    location=(82, 83),
                    active=True
                )
            ])
        )
        self.assertTrue(validate_global_preferences(json.loads(preferences_from_client)))

        preferences_from_client = json.dumps(dict(
            vehicles=['bus', 'subway'],
            personal_vehicles=[
                dict(
                    name="tesla",
                    type='car',
                    location=(13, 14),
                    active=True
                )
            ])
        )
        self.assertTrue(validate_global_preferences(json.loads(preferences_from_client)))

        calendar_from_client = json.dumps(dict(name='Home', description='Home sweet home', base=[50, 50],
                                               color=[243, 250, 152],
                                               active=True, carbon=True,
                                               preferences=[
                                                   dict(
                                                        name="bus",
                                                        time=['19:00', '20:30'],
                                                        mileage=10
                                                   ),
                                               ]))
        self.assertTrue(validate_calendar_data(json.loads(calendar_from_client)))

        calendar_from_client = json.dumps(dict(name='Home', description='Home sweet home', base=[50, 50],
                                               color=[243, 250, 152],
                                               active=True, carbon=True,
                                               preferences=[
                                                   dict(
                                                       name="bus",
                                                       time=['19:00', '20:30'],
                                                       mileage=0
                                                   )

                                               ]))
        self.assertFalse(validate_calendar_data(json.loads(calendar_from_client)))

        calendar_from_client = json.dumps(dict(name='Home', description='Home sweet home', base=[50, 50],
                                               color=[243, 250, 152],
                                               active=True, carbon=True,
                                               preferences=[
                                                   dict(
                                                       name="bus",
                                                       time=None,
                                                       mileage=None
                                                   )
                                               ]))
        self.assertTrue(validate_calendar_data(json.loads(calendar_from_client)))

        global_preferences = json.dumps(dict(
            vehicles=['bus', 'tram'],
            personal_vehicles=[
                dict(
                    name="tesla",
                    type='car',
                    location=[44.700546, 8.035837],
                    active=True
                )
                ]
            ))

        calendar_preferences = json.dumps([
            dict(
                name='bus',
                time=['19:00', '20:30'],
                mileage=10
            ),
            dict(
                name='tesla',
                time=None,
                mileage=200
            )
            ])
        self.assertTrue(validate_calendar_preferences(json.loads(calendar_preferences), json.loads(global_preferences)))

        calendar_preferences = json.dumps([
            dict(
                name='bus',
                time=None,
                mileage=None
            ),
            dict(
                name='bmx',
                time=None,
                mileage=10
            )
        ])
        self.assertFalse(validate_calendar_preferences(json.loads(calendar_preferences), json.loads(global_preferences)))

        calendar_preferences = json.dumps([
            dict(
                name='mobike',
                time=None,
                mileage=None
            )
        ])
        self.assertFalse(validate_calendar_preferences(json.loads(calendar_preferences), json.loads(global_preferences)))
