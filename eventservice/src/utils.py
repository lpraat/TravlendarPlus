import datetime
import json
import logging
import os
from contextlib import contextmanager
from logging import config

from dateutil.rrule import rrule
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from src.eventhandler import setup_channel_for_sending


def strptime(s):
    """
    Parses a string s formatted like %Y-%m-%d %H:%M:%S and returns the corresponding datetime.
    :param s: the string.
    :return: the datetime.
    """
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')


def strftime(t):
    """
    Given a datetime it returns the corresponding string in the format %Y-%m-%d %H:%M:%S.
    :param t: the datetime.
    :return: the string.
    """
    try:
        return t.strftime('%Y-%m-%d %H:%M:%S')
    except AttributeError:
        return t


def generate_occurrences(rec_rule, start_time, end_time, until):
    """
    Generates occurrences of start times and end times according to a recurrence rule. The occurrences are generated
    until the until date.

    :param rec_rule: the recurrence rule.
    :param start_time: the start datetime.
    :param end_time: the end datetime.
    :param until: the until datetime.
    :return: two lists containing respectively the start times and the end times of the occurrences.
    """
    start_occurrences = rrule(rec_rule, dtstart=start_time, until=until, cache=True)
    num_of_occurrences = len(list(start_occurrences))

    # here count optional parameter is used to have the same number of start and end times since there can be more
    # start times given an until date
    end_occurrences = rrule(rec_rule, dtstart=end_time, count=num_of_occurrences)
    return list(start_occurrences), list(end_occurrences)


@contextmanager
def session_scope(SessionType):
    session = SessionType()

    try:
        yield session
        session.commit()

    except:
        session.rollback()
        raise SQLAlchemyError

    finally:
        session.close()


def setup_logging(default_path='../logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """
    Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
            config['handlers']['info_file_handler']['filename'] = config['handlers']['info_file_handler']['filename']
            config['handlers']['error_file_handler']['filename'] = config['handlers']['error_file_handler']['filename']
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def get_sending_channel():
    """
    :return: the flask app sending channel if a flask app context is present, a new one otherwise.
    """
    if not current_app:
        return setup_channel_for_sending(app_ctx=False)
    return current_app.sending_channel
