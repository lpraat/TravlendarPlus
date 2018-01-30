from flask import Blueprint


query = Blueprint('query', __name__)


from src.queryhandler.get_user import handle_get