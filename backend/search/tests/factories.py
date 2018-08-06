import factory
from factory import Faker
from search import models
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from pytz import timezone
from django.conf import settings


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = Faker('safe_email')
    password = make_password('testing1234')
    first_name = Faker('first_name')
    last_name = Faker('last_name')
    is_staff = False
    is_superuser = False
    is_active = True
    date_joined = Faker('date_time_this_century', tzinfo=timezone(settings.TIME_ZONE))
    last_login = None


class FormFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Form

    name = Faker('company')
    section = Faker('bs')
