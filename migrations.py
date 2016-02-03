#!/usr/bin/env python
import os
import sys

""" 
Replaces manage.py for migrations.
"""

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "migrations_settings")

    from django.core.management import execute_from_command_line
    
    # we ensure the user is running "python migrations.py makemigrations rest_messaging"
    if all(arg in ['migrations.py', 'makemigrations', 'rest_messaging'] for arg in sys.argv[:3]):
        execute_from_command_line(sys.argv)
    else:
        raise Exception('Error: migrations.py may only be used to run migrations using: python migrations.py makemigrations rest_messaging')