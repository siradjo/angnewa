# angnewa/settings.py
import os

ENVIRONMENT = os.getenv('DJANGO_ENV', 'local')

if ENVIRONMENT == 'production':
    from .settings_production import *
else:
    from .settings_local import *
