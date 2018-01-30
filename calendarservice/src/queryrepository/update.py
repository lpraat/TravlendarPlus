from sqlalchemy.orm.attributes import flag_modified

from src.queryrepository import DBSession
from src.queryrepository.data.calendar import Calendar, GlobalPreferences
from src.utils import session_scope, make_calendar_preferences_consistent


def add_global_preferences(global_preferences):
    """
    Adds a global preferences to the database.
    :param global_preferences: the global preferences to be added.
    """
    with session_scope(DBSession) as session:
        session.add(global_preferences)


def modify_global_preferences(global_preferences):
    """
    Modifies the global preferences of a user in the database.
    :param global_preferences: the global preferences data needed for the update.
    """
    with session_scope(DBSession) as session:
        global_preferences_to_update = session.query(GlobalPreferences).filter(
            GlobalPreferences.user_id == global_preferences.user_id).first()

        global_preferences_to_update.preferences = global_preferences.preferences

        calendars = session.query(Calendar).filter(Calendar.user_id == global_preferences.user_id).all()

        # makes consistent all the user calendars according to the new global preferences
        gp = global_preferences.preferences
        for calendar in calendars:
            calendar.preferences = make_calendar_preferences_consistent(gp, calendar.preferences)
            flag_modified(calendar, "preferences")  # this is necessary to let postgresql note explicity that
                                                    # a json field has been changed


def delete_global_preferences(global_preferences):
    """
    Deletes the global preferences of a user in the database.
    :param global_preferences: the global preferences to be deleted.
    """
    with session_scope(DBSession) as session:
        global_preferences_to_delete = session.query(GlobalPreferences).filter(
            GlobalPreferences.user_id == global_preferences.user_id).first()
        session.delete(global_preferences_to_delete)


def add_calendar(calendar):
    """
    Adds a calendar to the database.
    :param calendar: the calendar to be added.
    """
    with session_scope(DBSession) as session:
        session.add(calendar)


def modify_calendar(calendar):
    """
    Modifies a calendar in the database.
    :param calendar: the calendar data needed for the update.
    """
    with session_scope(DBSession) as session:
        calendar_to_update = session.query(Calendar).filter(
            Calendar.user_id == calendar.user_id, Calendar.id == calendar.id).first()
        calendar_to_update.name = calendar.name
        calendar_to_update.description = calendar.description
        calendar_to_update.base = calendar.base
        calendar_to_update.color = calendar.color
        calendar_to_update.active = calendar.active
        calendar_to_update.carbon = calendar.carbon
        calendar_to_update.preferences = calendar.preferences


def delete_calendar(calendar):
    """
    Deletes a calendar in the database
    :param calendar: the calendar to be deleted.
    """
    with session_scope(DBSession) as session:
        calendar_to_delete = session.query(Calendar).filter(
            Calendar.user_id == calendar.user_id, Calendar.id == calendar.id).first()
        session.delete(calendar_to_delete)
