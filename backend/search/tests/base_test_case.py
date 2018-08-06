from rest_framework.test import APITestCase
from almanac.test_helpers import create_user


class BaseTestCase(APITestCase):
    def create_and_login_user(self):
        # create a user
        user = create_user()

        # log the user in
        self.client.credentials(
            HTTP_UID=user.username.upper(),
            HTTP_FNAME=user.first_name,
            HTTP_LNAME=user.last_name,
            HTTP_EMAIL=user.email
        )

        return user
