from flask import Blueprint


command = Blueprint('command', __name__)


from src.commandhandler.calendar_create import handle_create
from src.commandhandler.calendar_modify import handle_modify
from src.commandhandler.calendar_delete import handle_delete
from src.commandhandler.preferences_modify import handle_preferences