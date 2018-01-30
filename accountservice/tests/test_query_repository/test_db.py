from src.queryrepository.data.user import User
from src.queryrepository.update import add_user, modify_user, delete_user
from src.utils import hash_pass, check_pass, session_scope
from tests.test_app import TestApp


class TestQueryDB(TestApp):
    def test_user_db(self):
        with session_scope(self.DBSession) as session:
            session.add(User(id=1, email='pratissolil@gmail.com', password=hash_pass('test2'), first_name='test2', last_name='test2'))
            user = session.query(User).filter(User.email == 'pratissolil@gmail.com').first()
            self.assertTrue(check_pass('test2', user.password))

    def test_update_interface(self):
        user = User(id=2, email='prova@libero.it', password=hash_pass('prova'), first_name='prova', last_name='prova')
        add_user(user)
        modify_user(User(id=2, email='prova@libero.it', password=hash_pass('prova'), first_name='test', last_name='prova'))

        with session_scope(self.DBSession) as session:
            self.assertEqual(session.query(User).filter(User.email == 'prova@libero.it').first().first_name, 'test')

        delete_user(User(id=2))

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(User).filter(User.id == 2).first())
