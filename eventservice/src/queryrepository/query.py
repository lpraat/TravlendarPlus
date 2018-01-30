import copy

from src.queryrepository import DBSession
from src.queryrepository.data.event import Event, CalendarId, Recurrence
from src.utils import session_scope


def get_user_calendar_id(user_id, id):
    """
    Retrieves a user calendarid.
    :param user_id: the user id.
    :param id: the calendar id.
    :return: the calendarid.
    """
    with session_scope(DBSession) as session:
        calendar_id = session.query(CalendarId).filter(CalendarId.user_id == user_id, CalendarId.id == id).first()
        return copy.deepcopy(calendar_id)


def get_all_calendar_events(user_id, calendar_id):
    """
    Retrieves all the events on a user calendar
    :param user_id: the user id.
    :param calendar_id: the calendar id.
    :return: the list of tuples where each tuple contain an event and its recurrences.
    """
    with session_scope(DBSession) as session:
        events = session.query(Event).filter(Event.user_id == user_id, Event.calendar_id == calendar_id).all()

        return list((copy.deepcopy(event), get_event_recurrences(session, event)) for event in events)


def get_all_user_events(user_id):
    """
    Retrieves all the events of a user.
    :param user_id: the user id.
    :return: the list of tuples where each tuple contain an event and its recurrences.
    """
    with session_scope(DBSession) as session:
        events = session.query(Event).filter(Event.user_id == user_id).all()
        return list((copy.deepcopy(event), get_event_recurrences(session, event)) for event in events)


def get_event(user_id, calendar_id, id):
    """
    Retrieves a given event.
    :param user_id: the user id.
    :param calendar_id: the calendar id.
    :param id: the event id.
    :return: a tuple containing the event and its recurrences.
    """
    with session_scope(DBSession) as session:
        event = session.query(Event).filter(Event.user_id == user_id,
                                            Event.calendar_id == calendar_id,
                                            Event.id == id).first()
        return copy.deepcopy(event), get_event_recurrences(session, event)


def get_schedule(user_id):
    """
    Retrieves the schedule of a user.
    :param user_id: the user id.
    :return: the list of recurrences.
    """
    with session_scope(DBSession) as session:
        recurrences = session.query(Recurrence).filter(Recurrence.user_id == user_id).all()


        result = []
        for recurrence in recurrences:
            name = session.query(Event).filter(Event.user_id == recurrence.user_id,
                                                     Event.calendar_id == recurrence.calendar_id,
                                                     Event.id == recurrence.event_id).first().name

            result.append((copy.deepcopy(recurrence), name))

        return result


def get_event_recurrences(session, event):
    """
    Retrieves all the recurrences of an event coming from a session.
    :param session: the session.
    :param event: the event.
    :return: return the list of recurrences.
    """
    if event:
        recurrences = session.query(Recurrence).filter(Recurrence.user_id == event.user_id,
                                                       Recurrence.calendar_id == event.calendar_id,
                                                       Recurrence.event_id == event.id).all()
        return list(copy.deepcopy(recurrence) for recurrence in recurrences)
