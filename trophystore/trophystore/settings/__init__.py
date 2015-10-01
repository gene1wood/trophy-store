# If the app is launched with no DJANGO_SETTINGS_MODULE value, it will
# default to merely loading the "base" settings

from trophystore.settings.base import *

# If the app is launched with a DJANGO_SETTINGS_MODULE value, that
# settings file should import the base settings first in order to
# overlay them. An example import to be used in that settings file
# would be :
#
# from trophystore.settings.base import *
