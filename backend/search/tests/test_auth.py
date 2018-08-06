from .base_test_case import BaseTestCase
from rest_framework import status
from .factories import FormFactory
import json


class AuthTests(BaseTestCase):
    def test_auth_endpoints(self):
        # unauthorized not valid
        response = self.client.post('/api/v1/auth')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # create user and log them in
        user = self.create_and_login_user()

        # test successful endpoint
        response = self.client.post('/api/v1/auth')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json.loads(response.content).get('user_id'), user.id)

        # test invalid GET request
        response = self.client.get('/api/v1/auth')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test invalid PATCH request
        response = self.client.patch('/api/v1/auth')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test invalid PUT request
        response = self.client.put('/api/v1/auth')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # test invalid DELETE request
        response = self.client.delete('/api/v1/auth')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
