import os
import pytest
import site
import sys
from django.core.management import execute_from_command_line

os.environ['DJANGO_SETTINGS_MODULE'] = 'almanac.settings'
# from django.contrib.auth.models import User
# from search.models import *
# from search.tests import factories as search_facs
site.addsitedir(os.path.dirname(__file__))
pytestmark = pytest.mark.django_db
execute_from_command_line(sys.argv)
