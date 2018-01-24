from os import environ as env

DB_USER = env['DB_USER'] if 'DB_USER' in env else 'test'
DB_PASSWORD = env['DB_PASSWORD'] if 'DB_PASSWORD' in env else 'test'
DB_IP = env['DB_IP'] if 'DB_IP' in env else 'localhost'
DB_DB = env['DB_DB'] if 'DB_DB' in env else 'test'
DB_PORT = int(env['DB_PORT']) if 'DB_PORT' in env else 5432

EVENT_STORE_USER = env['EVENT_STORE_USER'] if 'EVENT_STORE_USER' in env else 'test'
EVENT_STORE_PASSWORD = env['EVENT_STORE_PASSWORD'] if 'EVENT_STORE_PASSWORD' in env else 'test'
EVENT_STORE_IP = env['EVENT_STORE_IP'] if 'EVENT_STORE_IP' in env else 'localhost'
EVENT_STORE_DB = env['EVENT_STORE_DB'] if 'EVENT_STORE_DB' in env else 'test'
EVENT_STORE_PORT = int(env['EVENT_STORE_PORT']) if 'EVENT_STORE_PORT' in env else 5433

RABBITMQ_IP = env['RABBITMQ_IP'] if 'RABBITMQ_IP' in env else 'localhost'
RABBITMQ_PORT = int(env['RABBITMQ_PORT']) if 'RABBITMQ_PORT' in env else 5672



