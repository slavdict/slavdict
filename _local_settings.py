# Rename this file to local_settings.py
# and use it to override the settings from settings.py
# in the current test site repository
# while keeping the original settings for the
# working site repository.
# File local_settings.py will be ignored
# by current git repository.

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     ROOT + '.temp.db',
    }
}

SITE_ID = 1
MEDIA_URL = 'http://127.0.0.1:8000/'
