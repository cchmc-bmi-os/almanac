"""
WSGI config for almanac project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

if os.path.isfile('settings_local.py'):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "almanac.settings_local")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "almanac.settings")

application = get_wsgi_application()
