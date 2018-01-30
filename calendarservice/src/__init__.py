from flask import Flask

from src.commandhandler import command
from src.log import log
from src.queryhandler import query
from src.utils import setup_logging


def create_app():
    """
    Creates the flask app and sets up logging.
    :return: the flask app.
    """
    calendarservice = Flask(__name__)
    setup_logging()
    return calendarservice


def register_blueprints(app):
    """
    Registers all blueprints to the app
    """
    app.register_blueprint(log)
    app.register_blueprint(command)
    app.register_blueprint(query)


