from flask import Blueprint


query = Blueprint('query', __name__)

from src.queryhandler.get_all_calendar_events import handle_get_all_calendar_events
from src.queryhandler.get_event import handle_get_event
from src.queryhandler.get_schedule import handle_get_schedule