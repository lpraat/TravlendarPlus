from flask import Blueprint

auth = Blueprint('auth', __name__)

from src.authenticationhandler.login import handle_login
