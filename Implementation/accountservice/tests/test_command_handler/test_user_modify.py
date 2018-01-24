import json

from src.queryrepository.data.user import User
from src.utils import session_scope
from tests.test_app import TestApp


class TestUserModify(TestApp):
    def test_user_modify(self):
        post_data = json.dumps(dict(
            email='test@test.it',
            password='test1234567',
            first_name='test',
            last_name='test')
        )
        id = json.loads(self.client.post('/users', data=post_data, content_type='application/json').data)['id']
        self.simulate_eventual_consistency()

        put_data = json.dumps(dict(
            email='test@test.it',
            password='prova12345678',
            first_name='test',
            last_name='test'
        ))
        response = self.client.put(f'/users/{id}', data=put_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(session.query(User).filter(User.id == 1).first().email, 'test@test.it')

        put_data = json.dumps(dict(
            email='test@test.it',
            password='prova',
            first_name='test',
            last_name='test'
        ))
        response = self.client.put(f'/users/{id}', data=put_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # password not valid
