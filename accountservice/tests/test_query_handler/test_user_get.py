import json

from tests.test_app import TestApp


class TestGetUser(TestApp):
    def test_user_get(self):
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

        response = self.client.get('/users/1')
        response_data = json.loads(response.data)
        self.assertEqual(response_data['id'], 1)
        self.assertEqual(response_data['email'], 'test@test.it')
        self.assertEqual(response_data['first_name'], 'test')
        self.assertEqual(response_data['last_name'], 'test')
