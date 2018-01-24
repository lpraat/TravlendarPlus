import json
import logging
import os
from contextlib import contextmanager
from logging import config

from flask import current_app
from sqlalchemy.exc import SQLAlchemyError

from src.eventhandler import setup_channel_for_sending


@contextmanager
def session_scope(SessionType):
    """
    Utils context manager to not write try except blocks every time.
    :param SessionType: the session the context manager is created for.
    """
    session = SessionType()

    try:
        yield session
        session.commit()

    except:
        session.rollback()
        raise SQLAlchemyError

    finally:
        session.close()


def make_calendar_preferences_consistent(global_preferences, preferences):
    """
    Makes calendar preferences consistent with the global preferences.
    :param global_preferences: the global preferences.
    :param preferences: the calendar preferences.
    :return: the new consistent calendar preferences.
    """
    new_preferences = preferences

    for vehicle in new_preferences[:]:
        if not (('vehicles' in global_preferences and vehicle['name'] in global_preferences['vehicles']) or
                    ('personal_vehicles' in global_preferences and vehicle['name'] in [p_vehicle['name'] for p_vehicle in global_preferences['personal_vehicles']])):
            new_preferences.remove(vehicle)

    return new_preferences


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
