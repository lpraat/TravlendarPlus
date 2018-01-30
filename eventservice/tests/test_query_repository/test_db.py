import datetime

from sqlalchemy.exc import SQLAlchemyError

from src.queryrepository.data.event import CalendarId
from src.queryrepository.data.event import Rrule, Event, Recurrence
from src.queryrepository.update import add_calendar_id, delete_calendar_id
from src.utils import session_scope
from tests.test_app import TestApp


class TestDB(TestApp):
    def test_event_db(self):
        with session_scope(self.DBSession) as session:
            session.add(CalendarId(user_id=1, id=1))

        def add_invalid_event():
            with session_scope(self.DBSession) as session:
                session.add(Event(user_id=1, calendar_id=2, id=1, name='Ultima Cena', location=[50, 40],
                                  start_time=datetime.datetime.now(),
                                  end_time=datetime.datetime.now() + datetime.timedelta(hours=3),
                                  recurrence_rule=Rrule.NORMAL,
                                  next_is_base=False,
                                  ))

        self.assertRaises(SQLAlchemyError, add_invalid_event)

        with session_scope(self.DBSession) as session:
            session.add(Event(user_id=1, calendar_id=1, id=1, name='Ultima Cena', location=[50, 40],
                              start_time=datetime.datetime.now(),
                              end_time=datetime.datetime.now() + datetime.timedelta(hours=3),
                              recurrence_rule=Rrule.NORMAL,
                              next_is_base=False,
                              ))

        def add_invalid_recurrence():
            with session_scope(self.DBSession) as session:
                session.add(Recurrence(user_id=1, calendar_id=1, event_id=3, id=1))

        self.assertRaises(SQLAlchemyError, add_invalid_recurrence)

        with session_scope(self.DBSession) as session:
            session.add(Recurrence(user_id=1, calendar_id=1, event_id=1, id=1))

        with session_scope(self.DBSession) as session:
            self.assertIsNotNone(
                session.query(Event).filter(Event.user_id == 1, Event.calendar_id == 1, Event.id == 1).first())
            self.assertIsNotNone(
                session.query(Recurrence).filter(Recurrence.user_id == 1, Recurrence.calendar_id == 1,
                                                 Recurrence.event_id == 1, Recurrence.id == 1).first())

    def test_on_delete_cascade(self):
        with session_scope(self.DBSession) as session:
            session.add(CalendarId(user_id=1, id=1))
            session.flush()
            for i in range(1, 10):
                session.add(Event(user_id=1, calendar_id=1, id=i, name=f'location {i}', location=[50, 40],
                                  start_time=datetime.datetime.now(),
                                  end_time=datetime.datetime.now() + datetime.timedelta(hours=3),
                                  recurrence_rule=Rrule.NORMAL,
                                  next_is_base=False,
                                  ))
            session.flush()
            for i in range(1, 10):
                session.add(Recurrence(user_id=1, calendar_id=1, event_id=1, id=i))
            session.flush()

            self.assertEqual(len(session.query(Event).all()), 9)
            self.assertEqual(len(session.query(Recurrence).all()), 9)
            session.delete(session.query(CalendarId).filter(CalendarId.user_id == 1, CalendarId.id == 1).first())
            self.assertIsNone(session.query(Event).first())
            self.assertIsNone(session.query(Recurrence).first())

    def test_update_interface(self):
        add_calendar_id(CalendarId(user_id=1, id=1))
        with session_scope(self.DBSession) as session:
            self.assertIsNotNone(session.query(CalendarId).filter(CalendarId.user_id == 1, CalendarId.id == 1).first())

        delete_calendar_id(CalendarId(user_id=1, id=1))
        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(CalendarId).filter(CalendarId.user_id == 1, CalendarId.id == 1).first())
