from threading import Thread

from src import create_app, register_blueprints
from src.eventhandler import setup_channel_for_receiving, setup_channel_for_sending
from src.eventhandler.event_receive import receive
from src.eventrepository import event_store_engine
from src.eventrepository.data.event import EventStoreBase
from src.queryrepository import db_engine
from src.queryrepository.data.user import DBBase

accountservice = create_app()
register_blueprints(accountservice)

DBBase.metadata.create_all(db_engine)                     # creates the database tables
EventStoreBase.metadata.create_all(event_store_engine)    # creates the event store tables

accountservice.sending_channel = setup_channel_for_sending()
accountservice.secret_key = '\x0c|f9\x91%1\xb2\xd2\xdd\xeeM\x15\xa1\xf1\xb09U\xb5Oj&\xe0M'  # generated with os.urandom(24)

# sets up a new thread listening for events coming from the message broker
listening_thread = Thread(target=receive, args=(setup_channel_for_receiving(),))  # sets up the thread listening to events
listening_thread.daemon = True
listening_thread.start()

if __name__ == '__main__':
    accountservice.run()
