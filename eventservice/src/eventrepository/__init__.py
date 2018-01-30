from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.configs import EVENT_STORE_USER, EVENT_STORE_PASSWORD, EVENT_STORE_IP, EVENT_STORE_PORT, EVENT_STORE_DB

# connects to the event store

event_store_engine = create_engine('postgresql://{0}:{1}@{2}:{3}/{4}'.format(EVENT_STORE_USER,
                                                                             EVENT_STORE_PASSWORD,
                                                                             EVENT_STORE_IP,
                                                                             EVENT_STORE_PORT,
                                                                             EVENT_STORE_DB))
EventStoreSession = sessionmaker(bind=event_store_engine)
