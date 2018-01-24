import json

import jwt

from tests.test_app import TestApp


class TestAuth(TestApp):
    def test_auth(self):
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

        res = self.client.post('/auth', headers=dict(Authorization=f'Bearer {token}'))
        self.assertEqual(json.loads(res.data)['id'], 1)

        res = self.client.post('/auth', headers=dict(Authorization=f'Bearer {token+"c"}'))
        self.assertEqual(res.status_code, 401)
