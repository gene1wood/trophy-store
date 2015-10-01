"""
WSGI config for trophystore project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""

import sys
import os

# Add the trophystore config directory to the path so that the
# local_settings.py file can be imported
sys.path.append("/etc/trophystore")

# Use local_settings.py as the settings file which in turn imports
# trophystore.settings.base and overlays localized settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
