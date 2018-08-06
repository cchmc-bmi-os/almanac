from django.contrib import auth
from django.contrib.auth import load_backend
from django.contrib.auth import ImproperlyConfigured
from django.contrib.auth.backends import RemoteUserBackend
from django.contrib.auth.middleware import RemoteUserMiddleware
from search.models import SavedCde


class HeaderAuthenticationMiddleware(RemoteUserMiddleware):
    header = 'HTTP_UID'

    def process_request(self, request):
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")

        try:
            username = request.META[self.header].lower()
        except KeyError:
            # If specified header doesn't exist then remove any existing
            # authenticated remote-user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).
            if request.user.is_authenticated:
                try:
                    stored_backend = load_backend(request.session.get(auth.BACKEND_SESSION_KEY, ''))
                    if isinstance(stored_backend, RemoteUserBackend):
                        auth.logout(request)
                except ImportError:
                    # backend failed to load
                    auth.logout(request)
            return

        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        # if request.user.is_authenticated():
        #    print request.user
        #    if request.user.get_username() == self.clean_username(username, request):
        #        return

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.
        user = auth.authenticate(remote_user=username)
        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.

            # update information from request
            try:
                user.first_name = request.META.get('HTTP_FNAME')
                user.last_name = request.META.get('HTTP_LNAME')
                user.email = request.META.get('HTTP_EMAIL').lower()
                user.username = user.username.lower()
                user.save()
            except:
                auth.logout(request)
                return

            # create an empty saved cde
            try:
                saved_cde = SavedCde.objects.get(user=user)
            except SavedCde.DoesNotExist:
                saved_cde = SavedCde.objects.create(
                    id=user.id,
                    user=user,
                    questions='[]'
                )
                saved_cde.save()

            request.user = user
            auth.login(request, user)
