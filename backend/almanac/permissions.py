from rest_framework import permissions
from django.conf import settings
from review.models import ReviewRole


UNAUTHENTICATED_VIEWS = [
    'auth_view',
    'search_user_log',
]

OBJECT_NEEDS_AUTH = [
    'Review',
    'ReviewRole',
    'ReviewVersion',
    'SavedCde',
    'User',
]

AUTH_ALLOW_POST = [
    'upload',
    'ReviewViewSet',
    'ReviewVersionViewSet',
    'expand_all',
    'collapse_all',
]


class DefaultPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        view_name = type(view).__name__
        # print(view_name)
        # print(request.user)
        # print(request.user.is_staff)
        if view_name in UNAUTHENTICATED_VIEWS:
            return True

        # must be authenticated
        if not request.user.is_authenticated:
            return False

        # if staff let them do it
        if request.user.is_staff:
            return True

        if view_name == 'SiteViewSet' and request.method == 'POST':
            # if the user is an admin role
            is_review_admin = ReviewRole.objects.filter(
                user=request.user,
                role=settings.DA_REVIEW_ADMIN_ROLE
            ).count() > 0

            return is_review_admin

        # if its a post and not in the allowed posts
        if view_name not in AUTH_ALLOW_POST and request.method == 'POST':
            return False


        # limit user listing
        if view_name == 'UserViewSet' or view_name == 'SavedCdeViewSet':
            if request.method == 'GET' and not request.path.split('/')[-1].isdigit():
                return False

        # for all others, handle at the object level
        return True

    def has_object_permission(self, request, view, obj):
        # if user is staff allow access
        if request.user.is_staff:
            return True

        object_type = type(obj).__name__

        # check to see if it a protected object
        if object_type in OBJECT_NEEDS_AUTH:
            # handle custom GET requests if any
            if request.method == 'GET' or request.method == 'OPTIONS':
                if object_type in ['SavedCde', 'Review', 'ReviewRole']:
                    return obj.user.id == request.user.id
                elif object_type == 'User':
                    return obj.id == request.user.id
                elif object_type == 'ReviewVersion':
                    return obj.review.user.id == request.user.id
                else:
                    return True

            # if the user is an admin role
            is_review_admin = ReviewRole.objects.filter(
                user=request.user,
                role=settings.DA_REVIEW_ADMIN_ROLE
            ).first()
            if is_review_admin:
                return True

            # handle the custom PATCH commands
            if request.method == 'PATCH':
                if object_type == 'Review':
                    return obj.user.id == request.user.id

                if object_type == 'ReviewVersion':
                    return obj.review.user.id == request.user.id

                if object_type == 'SavedCde':
                    return obj.user.id == request.user.id

            # handle the custom DELETE commands
            if request.method == 'DELETE':
                if object_type == 'Review':
                    return obj.user.id == request.user.id

            return False

        # if its a GET or OPTIONS, allow it
        if request.method == 'GET' or request.method == 'OPTIONS':
            return True

        return False
