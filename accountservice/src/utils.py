import json
import logging
import os
from contextlib import contextmanager
from logging import config

import bcrypt
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError


def hash_pass(password):
    """
    Hash a password using bcrypt using the default number of rounds.
    :param password: the password to be hashed.
    :return: the hashed password.
    """
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_pass(password, hashed_password):
    """

    :param password:
    :param hashed_password:
    :return:
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


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
    :return: the flask app sending channel set.
    """
    return current_app.sending_channel
