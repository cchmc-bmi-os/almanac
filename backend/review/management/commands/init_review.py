from django.core.management.base import BaseCommand
import sys
from django.contrib.auth.models import User
from review.models import ReviewRole
from django.conf import settings


class Command(BaseCommand):
    help = 'Initializes the review system'

    def add_arguments(self, parser):
        parser.add_argument('--admins', nargs='+', type=str)

    def handle(self, *args, **options):
        admin_users = options['admins']

        if not admin_users:
            response = input(
                'Are you sure you do not want to specify admins (Y/n)? ')

            if not response.lower() == 'y':
                print('Specify --admins [users]')
                sys.exit()
        else:
            for admin in admin_users:
                # try to find user
                user = User.objects.get(username=admin)

                for role in settings.DA_REVIEW_ROLES:
                    # try to find the user role
                    user_role = ReviewRole.objects.filter(
                        user=user, role=role).first()

                    if not user_role:
                        # create role if it doesn't exist
                        user_role = ReviewRole.objects.create(
                            user=user,
                            role=role
                        )
                        user.role.save()
