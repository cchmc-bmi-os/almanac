import os
from almanac.settings import *

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': os.path.join(BASE_DIR, 'almanac_test.sqlite')}}
HELP = {'EMAIL_TEXT': 'Provide Feedback to NBSTRN about CDEs', 'EMAIL': 'lpdr_nbstrn@acmg.net', 'EMAIL_SUBJECT': 'LPDR Data Almanac Feedback'}
DEBUG = True
APP_URL = 'http://localhost:4200'
BUGSNAG = {'enabled': False, 'app_version': '2.1.0', 'notify_release_stages': ['prod', 'test', 'dev'], 'endpoint': 'https://bugsnag-notify.research.cchmc.org', 'api_key': None, 'release_stage': 'ci'}
DEFAULT_FROM_EMAIL = 'help-lpdr@bmi.cchmc.org'
EMAIL_HOST = 'outbound-mail.cchmc.org'
DA_REVIEW_ROLES = ['CCHMC', 'ACMG']
DA_REVIEW_ADMIN_ROLE = 'CCHMC'
REVIEW_CONTACT_EMAIL = 'nicholas.felicelli@cchmc.org'
SECRET_KEY = '+1j*med+lj@tl%)w#vm50_ihsi1md+raz9f45z4ia6rcgaqtn-'
DATA_LOAD_DATE = '2017-09-11'
