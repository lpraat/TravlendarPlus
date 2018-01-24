from src.commandhandler.validate_data import RRULE
from src.queryrepository import DBSession
from src.queryrepository.data.event import CalendarId, Event, Recurrence
from src.utils import session_scope, strptime, generate_occurrences


def add_calendar_id(calendar_id):
    """
    Adds a new calendarid in the database.
    :param calendar_id: the calendarid to add.
    """
    with session_scope(DBSession) as session:
        session.add(calendar_id)


def delete_calendar_id(calendar_id):
    """
    Deletes a calendarid in the database.
    :param calendar_id: the calendarid to delete.
    """
    with session_scope(DBSession) as session:
        calendar_id_to_delete = session.query(CalendarId).filter(
            CalendarId.user_id == calendar_id.user_id, CalendarId.id == calendar_id.id
        ).first()
        session.delete(calendar_id_to_delete)


def delete_user_calendars(user_id):
    """
    Deletes all the user's calendarids in the database.
    :param user_id: the user id.
    """
    with session_scope(DBSession) as session:
        calendar_ids_to_delete = session.query(CalendarId).filter(
            CalendarId.user_id == user_id).all()

        if calendar_ids_to_delete: # user has atleast one calendar
            for calendar_id in calendar_ids_to_delete:
                session.delete(calendar_id)


def add_recurrences(session, event):
    """
    Given a session in which an event is being added to the database, it generates all the recurrences and add
    them to the database.
    :param session: the db session.
    :param event: the event the recurrences are generated for.
    """
    start_time = strptime(event.start_time)
    end_time = strptime(event.end_time)

    if event.recurrence_rule == 'NORMAL':
        session.add(
            Recurrence(user_id=event.user_id, calendar_id=event.calendar_id, event_id=event.id, id=1, start_time=start_time,
                       end_time=end_time))
    else:
        rec_rule = RRULE[event.recurrence_rule]['name']
        until = strptime(event.until)

        start_occurrences, end_occurrences = generate_occurrences(rec_rule, start_time, end_time, until)

        for i, (s_time, e_time) in enumerate(zip(start_occurrences, end_occurrences), 1):
            session.add(
                Recurrence(user_id=event.user_id, calendar_id=event.calendar_id, event_id=event.id, id=i, start_time=s_time,
                           end_time=e_time))
            session.flush()


def add_event(event):
    # add event + add all the to be generated recurrences
    """
    Adds a new event in the database with its recurrences.
    :param event: the event to be added.
    """
    with session_scope(DBSession) as session:
        session.add(event)
        session.flush()
        add_recurrences(session, event)


def modify_event(event):
    """
    Modifies an event in the database.
    :param event: the event data needed for the update.
    """
    with session_scope(DBSession) as session:
        for recurrence in session.query(Recurrence).filter(Recurrence.user_id == event.user_id,
                                                           Recurrence.calendar_id == event.calendar_id,
                                                           Recurrence.event_id == event.id):
            session.delete(recurrence)

        session.flush()

        event_to_update = session.query(Event).filter(Event.user_id == event.user_id,
                                                      Event.calendar_id == event.calendar_id,
                                                      Event.id == event.id).first()

        event_to_update.name = event.name
        event_to_update.location = event.location
        event_to_update.start_time = event.start_time
        event_to_update.end_time = event.end_time
        event_to_update.recurrence_rule = event.recurrence_rule
        event_to_update.until = event.until
        event_to_update.flex = event.flex
        event_to_update.flex_duration = event.flex_duration
        session.flush()

        add_recurrences(session, event)


def delete_event(event):
    """
    Deletes an event in the database.
    :param event: the event to delete.
    """
    with session_scope(DBSession) as session:
        event_to_delete = session.query(Event).filter(Event.user_id == event.user_id,
                                                      Event.calendar_id == event.calendar_id,
                                                      Event.id == event.id).first()
        session.delete(event_to_delete)


def delete_recurrence(recurrence):
    """
    Deletes a recurrence in the database.
    :param recurrence: the recurrence to delete.
    """
    with session_scope(DBSession) as session:
        recurrence_to_delete = session.query(Recurrence).filter(Recurrence.user_id == recurrence.user_id,
                                                                Recurrence.calendar_id == recurrence.calendar_id,
                                                                Recurrence.event_id == recurrence.event_id,
                                                                Recurrence.id == recurrence.id).first()
        session.delete(recurrence_to_delete)
