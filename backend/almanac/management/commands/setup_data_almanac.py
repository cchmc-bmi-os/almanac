from django.core.management.base import BaseCommand
import sys
from getpass import getpass
import random
from django.conf import settings
import os
from search.models import TagLabel
from django.core import management
from subprocess import call


class Command(BaseCommand):
    help = 'Sets up the data almanac to a default state'

    # default settings
    info = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': 'almanac_dev',
                'USER': 'root',
                'PASSWORD': 'secret',
                'HOST': 'localhost',
                'PORT': 5432,
            }
        },
        'HELP': {
            'EMAIL': 'lpdr_nbstrn@acmg.net',
            'EMAIL_TEXT': 'Provide Feedback to NBSTRN about CDEs',
            'EMAIL_SUBJECT': 'LPDR Data Almanac Feedback',
        },
        'DEBUG': True,
        'APP_URL': 'http://localhost:4200',
        'BUGSNAG': settings.BUGSNAG,
        'DEFAULT_FROM_EMAIL': 'help-lpdr@bmi.cchmc.org',
        'EMAIL_HOST': 'outbound-mail.cchmc.org',
        'DA_REVIEW_ROLES': 'CCHMC,ACMG',
        'DA_REVIEW_ADMIN_ROLE': 'CCHMC',
        'REVIEW_CONTACT_EMAIL': 'help-lpdr@bmi.cchmc.org',
        'DATA_LOAD_DATE': '2018-05-29'
    }

    local_settings = '{}/settings_local.py'.format(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )

    def add_arguments(self, parser):
        parser.add_argument('--use-default', action='store_true',
                            dest='use_default', help='Use default settings')

    def handle(self, *args, **options):
        self.use_defaults = options['use_default']

        if not os.path.isfile(self.local_settings):
            self.setup_settings()
            print("Please run the setup again to setup the database.")
            sys.exit()
        else:
            print('If you want to reset the settings, remove the settings_local.py file')

            sys.stdout.write('Loading latest data...')
            database = settings.DATABASES['default']['NAME']
            user = settings.DATABASES['default']['USER']
            password = settings.DATABASES['default']['PASSWORD']
            host = settings.DATABASES['default']['HOST']
            call([f'echo {password} | pg_restore -Fc -j 8 -O -d {database} -U {user} -h {host} almanac/fixtures/latest.dump'], shell=True)
            print('Done.')
            print('')

        print('Finished setting up Data Almanac')

    def setup_settings(self):
        self.info['SECRET_KEY'] = ''.join([random.SystemRandom().choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)])

        if not self.use_defaults:
            print('Database Settings: POSTGRES')
            tmp_settings = self.info.get('DATABASES').get('default')

            # get all the database connection information
            tmp_settings['HOST'] = input('  Database HOST ({}): '.format(tmp_settings.get('HOST'))) or tmp_settings.get('HOST')
            tmp_settings['PORT'] = input('  Database PORT ({}): '.format(tmp_settings.get('PORT'))) or tmp_settings.get('PORT')
            tmp_settings['NAME'] = input('  Database NAME ({}): '.format(tmp_settings.get('NAME'))) or tmp_settings.get('NAME')
            tmp_settings['USER'] = input('  Database USER ({}): '.format(tmp_settings.get('USER'))) or tmp_settings.get('USER')
            tmp_settings['PASSWORD'] = getpass(prompt='  Database PASSWORD ({}): '.format(tmp_settings.get('PASSWORD'))) or tmp_settings.get('PASSWORD')

            # save the updated information
            self.info['DATABASES']['default'] = tmp_settings

            print('')
            print('Help Settings:')
            tmp_settings = self.info.get('HELP')
            tmp_settings['EMAIL'] = input('  Enter help email address ({}): '.format(tmp_settings.get('EMAIL'))) or tmp_settings.get('EMAIL')
            tmp_settings['EMAIL_TEXT'] = input('  Enter text to display for help ({}): '.format(tmp_settings.get('EMAIL_TEXT'))) or tmp_settings.get('EMAIL_TEXT')
            tmp_settings['EMAIL_SUBJECT'] = input('  Enter the default subject for the help email ({}): '.format(tmp_settings.get('EMAIL_SUBJECT'))) or tmp_settings.get('EMAIL_SUBJECT')

            # save the updated information
            self.info['HELP'] = tmp_settings

            print('')
            print('Application Settings:')
            self.info['DEBUG'] = False if input('  Enable DEBUG flag? (Y/n): ').lower() in ['n', 'no'] else True
            self.info['APP_URL'] = input('  Where are you hosting the UI at? ({}): '.format(self.info.get('APP_URL'))) or self.info.get('APP_URL')

            print('')
            print('Bugsnag Settings:')
            tmp_settings = self.info.get('BUGSNAG')
            tmp_settings['enabled'] = True if input('  Enable bugsnag error reporting for dev, test, prod environments? (y/N): ').lower() in ['y', 'yes'] else False
            if tmp_settings['enabled']:
                tmp_settings['api_key'] = input('  Enter bugsnag api_key ({}): '.format(tmp_settings.get('api_key'))) or tmp_settings.get('api_key')
                tmp_settings['endpoint'] = input('  Enter bugsnag notify endpoint ({}): '.format(tmp_settings.get('endpoint'))) or tmp_settings.get('endpoint')
                tmp_settings['release_stage'] = input('  Enter application release_stage ({}): '.format(tmp_settings.get('release_stage'))) or tmp_settings.get('release_stage')

            # save the updated information
            self.info['BUGSNAG'] = tmp_settings

            print('')
            print('Email Settings:')
            self.info['DEFAULT_FROM_EMAIL'] = input('  Enter the from email you would like on outgoing email messages ({}): '.format(self.info.get('DEFAULT_FROM_EMAIL'))) or self.info.get('DEFAULT_FROM_EMAIL')
            self.info['EMAIL_HOST'] = input('  Enter the email host to send to ({}): '.format(self.info.get('EMAIL_HOST'))) or self.info.get('EMAIL_HOST')

            print('')
            print('Review Settings:')
            self.info['DA_REVIEW_ROLES'] = input('  Enter all the role names you want for the review: ({}): '.format(self.info.get('DA_REVIEW_ROLES'))) or self.info.get('DA_REVIEW_ROLES')
            self.info['DA_REVIEW_ROLES'] = self.info['DA_REVIEW_ROLES'].split(',')

            admin_role_valid = False
            while not admin_role_valid:
                admin_role = input('  Type in the role that should be the admin: ({}): '.format(self.info.get('DA_REVIEW_ADMIN_ROLE')))

                if admin_role == '':
                    admin_role = self.info.get('DA_REVIEW_ADMIN_ROLE')

                if admin_role in self.info['DA_REVIEW_ROLES']:
                    admin_role_valid = True
                else:
                    print('  Invalid admin role, it must be one of the ones you entered previously.')

            self.info['DA_REVIEW_ADMIN_ROLE'] = admin_role or self.info.get('DA_REVIEW_ROLES')
            self.info['REVIEW_CONTACT_EMAIL'] = input('  Enter the contact for the review system: ({}): '.format(self.info.get('REVIEW_CONTACT_EMAIL'))) or self.info.get('REVIEW_CONTACT_EMAIL')
        else:
            # all we need to do is convert the roles into a list
            self.info['DA_REVIEW_ROLES'] = self.info['DA_REVIEW_ROLES'].split(',')

        # write to file
        with open(self.local_settings, 'w') as file:
            file.write('from almanac.settings import *\n')
            for key, value in self.info.items():
                # print('{}: {} ({})'.format(key, value, type(value)))
                if type(value) == str:
                    file.write("{} = '{}'\n".format(key, value))
                else:
                    file.write("{} = {}\n".format(key, value))

    def setup_tags(self):
        sys.stdout.write('Creating question tags...')

        labels = [
            {'label': 'VarStatus', 'type': 'text', 'description': 'Variable status. This status reflects the status of the variable as it pertains to the search interface.  Consensus - reviewed by CIG and disease specific workgroup where applicable, Draft  - NBSTRN developed and not yet CIG reviewed, New = Researcher generated not reviewed by CIG yet, Retired = past consensus CDE no longer in use'},
            {'label': 'LpdrDefault', 'type': 'boolean', 'description': 'Indicates a default LPDR variable when more than one variable mapped back to a CDE.'},
            {'label': 'PI', 'type': 'text', 'description': 'Indicates the primary investigator.'},
            {'label': 'Instrument', 'type': 'text', 'description': 'Standardized collection instruments converted to work in REDCap.'},
            {'label': 'Identifier', 'type': 'boolean', 'description': 'If the question can be used for identifying a subject/participant and is considered PII.'},
            {'label': 'Required', 'type': 'boolean', 'description': 'If the question is required to be answered.'},
            {'label': 'Classification', 'type': 'text', 'description': 'Classification of each data element.'},
            {'label': 'CIGReview', 'type': 'boolean', 'description': 'Reviewed by the clinical integrations group (required for Core and Core(Required) tag)'},
            {'label': 'GUIDVar', 'type': 'boolean', 'description': 'Indicates the CDE is used to develop a GUID (nDAR).'},
        ]

        if not isinstance(self.info.get('DA_REVIEW_ROLES'), list):
            self.info['DA_REVIEW_ROLES'] = self.info.get('DA_REVIEW_ROLES').split(',')

        for role in self.info.get('DA_REVIEW_ROLES'):
            labels.append({'label': '{}Review'.format(role), 'type': 'boolean', 'description': 'Reviewed by {} (required for Core and Core(Required) tag)'.format(role)})

        for label in labels:
            newLabel = TagLabel(
                label=label.get('label'),
                type=label.get('type'),
                description=label.get('description'),
            )
            newLabel.save()

        print('Done.')
