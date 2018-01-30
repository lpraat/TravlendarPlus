import enum

from sqlalchemy import Column, Integer, String, ARRAY, Float, DateTime, ForeignKeyConstraint, Enum, Boolean
from sqlalchemy.ext.declarative import declarative_base

DBBase = declarative_base()


class CalendarId(DBBase):
    __tablename__ = 'calendarid'

    user_id = Column(Integer, autoincrement=False, primary_key=True)
    id = Column(Integer, autoincrement=False, primary_key=True)

    def __repr__(self):
        return f'<CalendarId(user_id={self.user_id}, id={self.id})>'


class Rrule(enum.Enum):
    YEARLY = 'YEARLY'
    MONTHLY = 'MONTHLY'
    WEEKLY = 'WEEKLY'
    DAILY = 'DAILY'
    NORMAL = 'NORMAL'


class Event(DBBase):
    __tablename__ = 'eventresource'

    user_id = Column(Integer, autoincrement=False, primary_key=True)
    calendar_id = Column(Integer, autoincrement=False, primary_key=True)
    id = Column(Integer, autoincrement=False, primary_key=True)
    name = Column(String(255))
    location = Column(ARRAY(Float))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    next_is_base = Column(Boolean)
    recurrence_rule = Column(Enum(Rrule))
    until = Column(DateTime)
    flex = Column(Boolean)
    flex_duration = Column(Float)

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "calendar_id"],
            ["calendarid.user_id", "calendarid.id"],
            ondelete='CASCADE'),
    )

    def __repr__(self):
        return f'<Event(user_id={self.user_id}, calendar_id={self.calendar_id}, id={self.id}>, '


class Recurrence(DBBase):
    __tablename__ = 'recurrence'

    user_id = Column(Integer, autoincrement=False, primary_key=True)
    calendar_id = Column(Integer, autoincrement=False, primary_key=True)
    event_id = Column(Integer, autoincrement=False, primary_key=True)
    id = Column(Integer, primary_key=True, autoincrement=False)
    start_time = Column(DateTime())
    end_time = Column(DateTime())

    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "calendar_id", "event_id"],
            ["eventresource.user_id", "eventresource.calendar_id", "eventresource.id"],
            ondelete='CASCADE'),
    )

    def __repr__(self):
        return f'<Recurrence(user_id={self.user_id}, calendar_id={self.calendar_id}, event_id={self.event_id}, ' \
               f'id={self.id}, start_time={self.start_time}, end_time={self.end_time}> '
