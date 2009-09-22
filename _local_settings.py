# Rename this file to local_settings.py 
# and use it to override the settings from settings.py
# in the current test site repository 
# while keeping the original settings for the
# working site repository.
# File local_settings.py will be ignored
# by current git repository.

DEBUG = True
ROOT = 'D:/workplace/git_repositories/iasp'
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'D:/workplace/sqlite-dbs/iasp-django.db'
SITE_ID = 1
MEDIA_URL = 'http://127.0.0.1:8000/'
