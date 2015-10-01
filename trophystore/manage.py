#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    # Add the trophystore config directory to the path so that the
    # local_settings.py file can be imported
    sys.path.append("/etc/trophystore")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "local_settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
