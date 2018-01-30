from os import environ as env

DB_USER = env['DB_USER'] if 'DB_USER' in env else 'postgres'
DB_PASSWORD = env['DB_PASSWORD'] if 'DB_PASSWORD' in env else 'admin'
DB_IP = env['DB_IP'] if 'DB_IP' in env else 'localhost'
DB_PORT = int(env['DB_PORT']) if 'DB_PORT' in env else 5432
DB_DB = env['DB_DB'] if 'DB_DB' in env else 'production'

DEBUG = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_BINDS = {
    'instructions': f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_IP}:{DB_PORT}/{DB_DB}"
}