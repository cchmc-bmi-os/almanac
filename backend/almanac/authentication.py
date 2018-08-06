from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions


class HeaderAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        # try to get all the headers
        try:
            user_data = {
                'username': request.META['HTTP_UID'].lower(),
                'first_name': request.META['HTTP_FNAME'],
                'last_name': request.META['HTTP_LNAME'],
                'email': request.META['HTTP_EMAIL'].lower()
            }
        except:
            raise exceptions.AuthenticationFailed('Invalid headers')

        # try to get the user object
        try:
            user = User.objects.get(username=user_data.get('username'))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
