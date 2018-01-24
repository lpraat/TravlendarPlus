from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.configs import DB_USER, DB_PASSWORD, DB_IP, DB_PORT, DB_DB

# connects to the database
db_engine = create_engine('postgresql://{0}:{1}@{2}:{3}/{4}'.format(DB_USER,
                                                                    DB_PASSWORD,
                                                                    DB_IP,
                                                                    DB_PORT,
                                                                    DB_DB))

DBSession = sessionmaker(bind=db_engine)
