from sqlalchemy import Column, String, Integer, JSON,Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.declarative import declarative_base

DBBase = declarative_base()


class GlobalPreferences(DBBase):
    __tablename__ = 'globalpreferences'

    user_id = Column(Integer, autoincrement=False, primary_key=True)
    preferences = Column(JSON)

    def __repr__(self):
        return f'<GlobalPreferences(user_id={self.user_id}, preferences={self.preferences}'


class Calendar(DBBase):
    __tablename__ = 'calendarresource'

    user_id = Column(Integer, ForeignKey('globalpreferences.user_id', ondelete='CASCADE'), autoincrement=False, primary_key=True)
    id = Column(Integer, primary_key=True, autoincrement=False)
    name = Column(String(255), unique=True)
    description = Column(String(255))
    base = Column(ARRAY(Float))
    color = Column(ARRAY(Integer))
    active = Column(Boolean)
    carbon = Column(Boolean)
    preferences = Column(JSON)

    def __repr__(self):
        return f'<Calendar(user_id={self.user_id}, id={self.id}, name={self.name}, description={self.description}, base={self.base}, ' \
               f'color={self.color}, active={self.active}, carbon={self.carbon}, preferences={self.preferences}>'
