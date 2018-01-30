import copy

from src.queryrepository import DBSession
from src.queryrepository.data.user import User
from src.utils import check_pass
from src.utils import session_scope


def get_user_id_by_credentials(email, password):
    """
    Retrieves a user from the database given the credentials.
    :param email: the email of the user.
    :param password: the password of the user.
    :return: the user id.
    """
    with session_scope(DBSession) as session:
        user = session.query(User).filter(User.email == email).first()
        if user:
            if check_pass(password, user.password):
                return user.id


def get_user_by_id(id):
    """
    Retrieves a user from the database given the id.
    :param id: the user id.
    :return: the user id.
    """
    with session_scope(DBSession) as session:
        user = session.query(User).filter(User.id == id).first()
        return copy.deepcopy(user)