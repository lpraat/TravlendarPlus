import json
import logging
from enum import Enum

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import TypeDecorator, VARCHAR

logger = logging.getLogger(__name__)
db = SQLAlchemy()


class TravelMode(Enum):
    DRIVING = 0
    WALKING = 1
    BICYCLING = 2
    TRANSIT = 3

class TransitType(Enum):
    BUS = 0
    SUBWAY = 1
    TRAIN = 2
    TRAM = 3
    HEAVY_RAIL = 4


class JSONEncodedDict(TypeDecorator):
    """
    Represents an immutable structure as a json-encoded string.
    """
    impl = VARCHAR

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class GlobalPreference(db.Model):
    __tablename__ = 'preferences'
    __bind_key__ = 'instructions'

    user_id = db.Column(db.Integer, primary_key=True)
    vehicles = db.Column(JSONEncodedDict())
    personal_vehicles = db.Column(JSONEncodedDict())


class Calendar(db.Model):
    __tablename__ = 'calendars'
    __bind_key__ = 'instructions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('preferences.user_id', ondelete='CASCADE'), primary_key=True)
    global_preferences = db.relationship('GlobalPreference', backref=db.backref('calendars', cascade='delete'))
    name = db.Column(db.String())
    description = db.Column(db.String())
    base = db.Column(JSONEncodedDict())
    color = db.Column(JSONEncodedDict())
    active = db.Column(db.Boolean)
    carbon = db.Column(db.Boolean)
    preferences = db.Column(JSONEncodedDict())


class TripDetail(db.Model):
    """
    Base class for every table that contains info about a trip.
    """
    __abstract__ = True
    __bind_key__ = 'instructions'

    id = db.Column(db.Integer, primary_key=True)
    start_lat = db.Column(db.Float)
    start_lng = db.Column(db.Float)
    end_lat = db.Column(db.Float)
    end_lng = db.Column(db.Float)
    distance = db.Column(db.Integer)
    duration = db.Column(db.Integer)
    polyline = db.Column(db.String())  # line to plot

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Overview(TripDetail):
    """
    Class that contains general information about a trip.
    """
    __tablename__ = 'overviews'
    __table_args__ = (
        db.ForeignKeyConstraint(['user_id', 'calendar_id'], ['calendars.user_id', 'calendars.id'], ondelete='CASCADE'),
    )
    user_id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, primary_key=True)
    departure = db.Column(db.Boolean, primary_key=True, default=True)  # False if the indications are reversed
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    reachable = db.Column(db.Boolean, nullable=False, default=True)
    start_address = db.Column(db.String())
    end_address = db.Column(db.String())
    bounds = db.Column(JSONEncodedDict())
    cached = db.Column(db.Boolean)
    flex_duration = db.Column(db.Integer, default=None)
    next_is_base = db.Column(db.Boolean, default=False)
    calendar = db.relationship('Calendar', backref=db.backref('overviews', cascade='delete'), passive_deletes=True)


class Step(TripDetail):
    """
    When driving, a trip is split into different steps each time the type of the road changes. In TRANSIT mode, each
    travel mean route has its own step (and same works for walking paths).
    """
    __tablename__ = 'steps'
    __table_args__ = (
        db.ForeignKeyConstraint(['overview_id', 'user_id', 'calendar_id', 'event_id', 'departure'],
                                ['overviews.id', 'overviews.user_id', 'overviews.calendar_id', 'overviews.event_id', 'overviews.departure'],
                                ondelete='CASCADE'),
    )
    overview_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    calendar_id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, primary_key=True)
    departure = db.Column(db.Boolean, primary_key=True, default=True)
    overview = db.relationship('Overview', backref=db.backref('steps', cascade='delete'))
    instructions = db.Column(db.String(), nullable=False)  # html instructions to complete this step.
    travel_mode = db.Column(db.Enum(TravelMode), nullable=False)
    # details present only if the travel_mode is 'TRANSIT'
    line_name = db.Column(db.String())
    type = db.Column(db.Enum(TransitType))
    num_stops = db.Column(db.SmallInteger)
    departure_stop = db.Column(db.String())
    departure_time = db.Column(db.DateTime)
    arrival_stop = db.Column(db.String())
    arrival_time = db.Column(db.DateTime)
