import logging

from models import Overview

logger = logging.getLogger(__name__)


def get_overviews_by_date(user_id, start, end, departure_only=False, return_only=False):
    """Returns overviews between the given dates"""
    logger.info(f"Requesting overviews between {start} and {end}")
    if departure_only and return_only:  # both preferences cannot be satisfied
        raise ValueError
    overviews = Overview.query.filter(Overview.user_id == user_id,
                                      Overview.start_date > start,
                                      Overview.start_date < end).all()
    return [overview for overview in overviews if not (return_only and overview.departure) and
            not (departure_only and not overview.departure)]


def get_all_daily(user_id, date, departure_only=False, return_only=False):
    """Gets all events on the same day of the overview passed as parameter"""
    day_start = date.replace(hour=0, minute=0, second=0)
    day_end = date.replace(hour=23, minute=59, second=59)
    return get_overviews_by_date(user_id, day_start, day_end, departure_only=departure_only, return_only=return_only)


def get_previous_daily(user_id, date, departure_only=True):
    """Gets events on the same day of the date passed as parameter that start before it"""
    day_start = date.replace(hour=0, minute=0, second=0)
    return sorted(get_overviews_by_date(user_id, day_start, date, departure_only=departure_only), key=lambda o: o.start_date)


def get_incoming_daily(user_id, date, departure_only=True):
    """Gets events on the same day of the date passed as parameter that start after it"""
    day_end = date.replace(hour=23, minute=59, second=59)
    return sorted(get_overviews_by_date(user_id, date, day_end, departure_only=departure_only), key=lambda o: o.start_date)


def get_all_sorted(user_id):
    logger.info(f"Requesting all overviews for user {user_id}")
    overviews = Overview.query.filter_by(user_id=user_id).all()
    return sorted(overviews, key=lambda o: o.start_date)


def get_all_calendar(user_id, calendar_id):
    overviews = Overview.query.filter_by(user_id=user_id, calendar_id=calendar_id).all()
    return overviews


def get_all_recurrences(info, user_id):
    overviews = Overview.query.filter_by(user_id=user_id,  # gets all recurrences for this event
                                         calendar_id=info['calendar_id'],
                                         event_id=info['id'],
                                         departure=True).all()
    return sorted(overviews, key=lambda o: o.start_date)