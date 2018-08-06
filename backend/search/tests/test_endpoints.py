from .base_test_case import BaseTestCase
from rest_framework import status
from .factories import FormFactory
import json


class EndpointTests(BaseTestCase):
    def test_forms_endpoints(self):
        # unauthorized not valid
        response = self.client.get('/api/v1/forms')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        user = self.create_and_login_user()

        # # POST not valid
        response = self.client.post('/api/v1/forms')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # PATCH not valid
        response = self.client.patch('/api/v1/forms')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # PUT not valid
        response = self.client.put('/api/v1/forms')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # DELETE not valid
        response = self.client.delete('/api/v1/forms')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        # LIST is valid
        response = self.client.get('/api/v1/forms')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # GET is valid
        form = FormFactory()
        print(form)
        print(form.id, form.name, form.section)

        response = self.client.get('/api/v1/forms/{}'.format(form.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        print(json.loads(response.content))
        self.assertEqual(json.loads(response.content).get('data').get('id'), form.id)

