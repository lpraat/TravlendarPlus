from src.queryrepository import DBSession
from src.queryrepository.data.user import User
from src.utils import session_scope


def add_user(user):
    """
    Adds a user to the database.
    :param user: the user to add.
    """
    with session_scope(DBSession) as session:
        session.add(user)


def modify_user(user):
    """
    Modifies a user in the database.
    :param user: the user data to insert.
    """
    with session_scope(DBSession) as session:
        user_to_update = session.query(User).filter(User.id == user.id).first()
        user_to_update.email = user.email
        user_to_update.password = user.password
        user_to_update.first_name = user.first_name
        user_to_update.last_name = user.last_name


def delete_user(user):
    """
    Deletes a user in the database
    :param user: the user to delete.
    """
    with session_scope(DBSession) as session:
        user_to_delete = session.query(User).filter(User.id == user.id).first()
        session.delete(user_to_delete)
