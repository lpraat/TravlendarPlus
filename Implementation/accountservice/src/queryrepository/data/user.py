from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base

DBBase = declarative_base()


class User(DBBase):
    __tablename__ = 'userresource'

    id = Column(Integer, primary_key=True, autoincrement=False)
    email = Column(String(255), unique=True)
    password = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))

    def __repr__(self):
        return f'<User(id={self.id}, email={self.email}, ' \
               f'password={self.password}, first_name={self.first_name}, ' \
               f'last_name={self.last_name}>'