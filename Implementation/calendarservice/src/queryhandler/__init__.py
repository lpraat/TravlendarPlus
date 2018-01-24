from flask import Blueprint


query = Blueprint('query', __name__)


from src.queryhandler.get_all_calendars import handle_get_all_calendars
from src.queryhandler.get_calendar import handle_get_calendar
from src.queryhandler.get_global_preferences import handle_get_global_preferences