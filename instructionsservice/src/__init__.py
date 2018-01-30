import json
import logging
import logging.config
import os
from threading import Thread

from flask import Flask

from handler import setup_sending_channel, receive, setup_receiving_channel
from instructions import instructions
from models import db


def create_app(config='config'):
    # Flask
    app = Flask(__name__)
    app.config.from_object(config)
    app.register_blueprint(instructions)
    # Flask-SQLAlchemy
    app.app_context().push()
    db.init_app(app)
    db.create_all()
    # RabbitMQ
    app.sending_channel = setup_sending_channel()
    app.secret_key = '\x0c|f9\x91%1\xb2\xd2\xdd\xeeM\x15\xa1\xf1\xb09U\xb5Oj&\xe0M'
    listening_thread = Thread(target=receive, args=(setup_receiving_channel(), app))
    listening_thread.daemon = True
    listening_thread.start()
    return app


def setup_logging(path='../logging.json', default_level=logging.INFO, env_key='LOG_CFG', tofile=True):
    """
    Setup logging configuration
    """
    path = path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
            if not tofile:
                config['root']['handlers'] = ['console']  # keeps only console
                config['handlers'] = {'console': config['handlers']['console']}
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)