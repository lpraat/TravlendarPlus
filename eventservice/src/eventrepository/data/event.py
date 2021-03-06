import copy

from sqlalchemy import Column, String, JSON
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base

from src.eventrepository import EventStoreSession
from src.utils import session_scope

EventStoreBase = declarative_base()


class EventEvent(EventStoreBase):
    """
    The event stored in the event store.
    Every event is globally identified by a uuid.
    """
    __tablename__ = 'eventevent'

    uuid = Column(String, primary_key=True, autoincrement=False)
    timestamp = Column(TIMESTAMP, server_default=func.now(), unique=True)
    event = Column(JSON)

    def __repr__(self):
        return '<EventEvent(uuid={0}, timestamp={1}, data={2}'.format(self.id, self.timestamp, self.event)

    @classmethod
    def get_all_events(cls):
        with session_scope(EventStoreSession) as session:
            return copy.deepcopy(session.query(cls).all())

    @classmethod
    def append_event(cls, event):
        with session_scope(EventStoreSession) as session:
            session.add(cls(uuid=event.uuid, event=event.toJSON()))
