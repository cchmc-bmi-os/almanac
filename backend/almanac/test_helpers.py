from django.contrib.auth.models import User
from search.tests.factories import UserFactory


def create_user():
    user = UserFactory()

    # hash a known password
    user.set_password('testing1234')
    user.save()

    return user
