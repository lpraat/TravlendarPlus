import json

from sqlalchemy.exc import SQLAlchemyError

from src.queryrepository.data.calendar import GlobalPreferences, Calendar
from src.queryrepository.update import add_global_preferences, modify_global_preferences, add_calendar, modify_calendar, \
    delete_calendar
from src.utils import session_scope
from tests.test_app import TestApp


class TestQueryDB(TestApp):
    def test_calendar_db(self):
        with session_scope(self.DBSession) as session:
            session.add(GlobalPreferences(
                user_id=1,
                preferences=json.dumps(dict(
                    vehicles=['bus'],
                    personal_vehicles=[
                        dict(
                            name='tesla',
                            type='car',
                            location=(44.700546, 8.035837),
                            active=True
                        )
                    ]))))

        def add_invalid_calendar():
            with session_scope(self.DBSession) as session:
                session.add(
                    Calendar(user_id=2, id=1, name='Lavoro', description='Full Stack', base=[50.700546, 10.035837],
                             color=[255, 255, 255], active=True, carbon=False,
                             preferences=[dict(
                                 name='bus',
                                 time=None,
                                 mileage=10
                             )]))

        # there is no user_id 2
        self.assertRaises(SQLAlchemyError, add_invalid_calendar)

        with session_scope(self.DBSession) as session:
            session.add(Calendar(
                user_id=1, id=1, name='Lavoro', description='Full Stack', base=[50.700546, 10.035837],
                color=[255, 255, 255], active=True, carbon=False,
                preferences=[dict(
                    name='bus',
                    time=None,
                    mileage=10
                )]))

        with session_scope(self.DBSession) as session:
            self.assertIsNotNone(session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 1).first())
            self.assertIsNotNone(session.query(Calendar).filter(Calendar.name == 'Lavoro').first())

    def test_on_delete_cascade(self):
        with session_scope(self.DBSession) as session:
            session.add(GlobalPreferences(
                user_id=1,
                preferences=json.dumps(dict(
                    vehicles=['bus'],
                    personal_vehicles=[dict(
                        name='tesla',
                        type='car',
                        location=(44.700546, 8.035837),
                        active=True
                    )]
                ))))
            session.flush()
            for i in range(1, 10):
                session.add(Calendar(
                    user_id=1, id=i, name=f'Lavoro{i}', description='Full Stack', base=[50.700546, 10.035837],
                    color=[255, 255, 255], active=True, carbon=False,
                    preferences=[dict(
                        name='bus',
                        time=None,
                        mileage=10
                    )]))
            session.flush()

            self.assertEqual(len(session.query(Calendar).all()), 9)
            session.delete(session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 1).first())
            self.assertIsNone(session.query(Calendar).first())

    def test_update_interface(self):
        add_global_preferences(GlobalPreferences(
            user_id=734,
            preferences=json.dumps(dict(
                vehicles=['bus', 'enjoy', 'mobike'],
                personal_vehicles=[dict(
                    name='tesla',
                    type='car',
                    location=(44.700546, 8.035837),
                    active=True
                )]))))

        modify_global_preferences(GlobalPreferences(
            user_id=734,
            preferences=json.dumps(dict(
                vehicles=['bus', 'enjoy', 'mobike'],
                personal_vehicles=[
                    dict(
                        name='tesla',
                        type='car',
                        location=(44.700546, 8.035837),
                        active=True
                    ),
                    dict(
                        name='bmx',
                        type='bike',
                        location=(44.700546, 8.035837),
                        active=False
                    )]
            ))))

        with session_scope(self.DBSession) as session:
            self.assertIsNotNone(
                json.loads(session.query(GlobalPreferences).filter(GlobalPreferences.user_id == 734)
                           .first().preferences)['personal_vehicles'][1])

        add_calendar(Calendar(user_id=734, id=1, name='Job', description='', base=[50.700546, 10.035837],
                              color=[248, 255, 248], active=True, carbon=False,
                              preferences=[dict(
                                  name='bus',
                                  time=None,
                                  mileage=10
                              )]))

        modified_calendar = Calendar(user_id=734, id=1, name='Job', description='new description',
                                     base=[50.700546, 10.035837],
                                     color=[248, 255, 248], active=True, carbon=False,
                                     preferences=[dict(
                                         name='bus',
                                         time=None,
                                         mileage=10
                                     )])
        modify_calendar(modified_calendar)

        with session_scope(self.DBSession) as session:
            self.assertEqual(
                session.query(Calendar).filter(Calendar.user_id == 734 and Calendar.id == 1).first().description,
                modified_calendar.description
            )

        delete_calendar(Calendar(user_id=734, id=1))

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(Calendar).filter(Calendar.user_id == 734 and Calendar.id == 1).first())
