import copy

from src.queryrepository import DBSession
from src.queryrepository.data.calendar import Calendar, GlobalPreferences
from src.utils import session_scope


def get_all_user_calendars(user_id):
    """
    Retrieves all the calendars of a given user.
    :param user_id: the user id.
    :return: the list of the calendars of the user.
    """
    with session_scope(DBSession) as session:
        calendars = session.query(Calendar).filter(Calendar.user_id == user_id).all()
        return list(copy.deepcopy(calendar) for calendar in calendars)


def get_calendar(user_id, id):
    """
    Retrieves a user calendar.
    :param user_id: the user id.
    :param id: the calendar id.
    :return: the calendar.
    """
    with session_scope(DBSession) as session:
        calendar = session.query(Calendar).filter(Calendar.user_id == user_id, Calendar.id == id).first()
        return copy.deepcopy(calendar)


def get_user_global_preferences(user_id):
    """
    Retrieves a user global preferences.
    :param user_id: the user id.
    :return: the global preferences of the user.
    """
    with session_scope(DBSession) as session:
        global_preferences = session.query(GlobalPreferences).filter(GlobalPreferences.user_id == user_id).first()
        return copy.deepcopy(global_preferences)