import json

from src.queryrepository.data.user import User
from src.utils import session_scope
from tests.test_app import TestApp


class TestUserCreate(TestApp):
    def test_user_create(self):
        post_data = json.dumps(dict(
            email='test@test.it',
            password='test1234567',
            first_name='test',
            last_name='test')
        )
        response = self.client.post('/users', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(json.loads(response.data)['id'], 1)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(session.query(User).filter(User.id == 1).first().email, 'test@test.it')

        post_data = json.dumps(dict(
            email='prova@prova.it',
            password='prova123123123',
            first_name='prova',
            last_name='prova'
        ))
        response = self.client.post('/users', data=post_data, content_type='application/json')
        self.assertEqual(json.loads(response.data)['id'], 2)
        self.simulate_eventual_consistency()

        with session_scope(self.DBSession) as session:
            self.assertEqual(session.query(User).filter(User.id == 2).first().email, 'prova@prova.it')
