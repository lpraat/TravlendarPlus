import json

from src.queryrepository.data.user import User
from src.utils import session_scope
from tests.test_app import TestApp


class TestUserDelete(TestApp):
    def test_user_delete(self):
        post_data = json.dumps(dict(
            email='test@test.it',
            password='test1234567',
            first_name='test',
            last_name='test')
        )
        id = json.loads(self.client.post('/users', data=post_data, content_type='application/json').data)['id']
        self.simulate_eventual_consistency()

        self.client.delete(f'/users/{id}')
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertIsNone(session.query(User).filter(User.id == 1).first())
