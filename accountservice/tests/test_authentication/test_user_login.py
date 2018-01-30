import json

import jwt

from tests.test_app import TestApp


class TestUserLogin(TestApp):
    def test_user_login(self):
        post_data = json.dumps(dict(
            email='test@test.it',
            password='test1234567',
            first_name='test',
            last_name='test')
        )
        id = json.loads(self.client.post('/users', data=post_data, content_type='application/json').data)['id']
        self.simulate_eventual_consistency()

        post_data = json.dumps(dict(
            email='test@test.it',
            password='test1234567'
        ))
        response = self.client.post('/login', data=post_data, content_type='application/json')
        token = json.loads(response.data)['auth_token']
        self.assertEqual(id, jwt.decode(token, self.app.secret_key, algorithms='HS256')['sub'])

        post_data = json.dumps(dict(
            email='test@test.it',
            password='pippo23123123',
        ))
        response = self.client.post('/login', data=post_data, content_type='application/json')
        self.assertEqual(response.status_code, 400)  # user is not registered
