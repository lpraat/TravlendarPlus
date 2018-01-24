from flask import Blueprint


command = Blueprint('command', __name__)


from src.commandhandler.user_create import handle_create
from src.commandhandler.user_modify import handle_modify
from src.commandhandler.user_delete import handle_delete