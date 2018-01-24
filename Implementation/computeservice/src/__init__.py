import json
import logging
import logging.config
import os
from os import environ as env
import redis
from flask import Flask, Blueprint

REDIS_IP = env['REDIS_IP'] if 'REDIS_IP' in env else 'localhost'
REDIS_PORT = int(env['REDIS_PORT']) if 'REDIS_PORT' in env else 6379
r = redis.StrictRedis(host=REDIS_IP, port=REDIS_PORT, db=0, decode_responses=True)
compute = Blueprint('compute', __name__)
from directions import get_directions


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
        print("couldn't find path")
        logging.basicConfig(level=default_level)


def create_app():
    app = Flask(__name__)
    app.config.from_object('config')
    app.register_blueprint(compute)
    return app
