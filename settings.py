# -*- coding: UTF-8 -*-
# Django settings for slavdict project.
import os

slash = '/'
backslash = '\\'

# Базовые настройки проекта,
# от которых могут зависеть другие настройки
DEBUG = False
ROOT = os.path.normpath( os.path.abspath( os.path.dirname( __file__ ) ) ).replace( backslash, slash ) + slash

# Локальное переопределение базовых настроек,
# если оно имеется.
try:
    from local_base_settings import *
except ImportError:
    pass

# Настройки, зависящие от базовых
# либо от которых не зависят другие настройки.
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('khitrov', 'a.n.khitrov@gmail.com'),
)
MANAGERS = ADMINS
BACKUP_MANAGERS = MANAGERS + (
    ('imperfect', 'imperfect@yandex.ru'),
)
SERVER_EMAIL = 'no-reply@slavdict.ruslang.ru'
INTERNAL_IPS = ('127.0.0.1',)

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     ROOT + '.test.db',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_URL = '/logout/'

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ROOT + 'media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/u/'

STATIC_ROOT = ROOT + '.static/'
STATIC_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'td2+2t^tz-)^j^%@4_^c8ds#6-po3sfoqbwaa2u*i3rj3y%hs1'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
)

#from jinja2 import StrictUndefined
JINJA2_ENVIRONMENT_OPTIONS = {
    'autoescape': False,
#    'undefined': StrictUndefined,
}

JINJA2_EXTENSIONS = (
    'slavdict.django_template_spaces.templatetags.trim_spaces.trim',
)

MIDDLEWARE_CLASSES = (
    'slavdict.middleware.CookieVersionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'slavdict.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT + 'templates/',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.debug',
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

STATICFILES_DIRS = (
    ROOT + 'static/',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.staticfiles',
    'django.contrib.messages',

    'slavdict.dictionary',
    'slavdict.custom_user',
    'slavdict.django_template_spaces',

    'south',
    'coffin',
)

######################################
##  Настройки отдельных приложений  ##
######################################

# custom_user
AUTHENTICATION_BACKENDS = (
    'slavdict.auth_backends.CustomUserModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)
CUSTOM_USER_MODEL = 'custom_user.CustomUser'


# Локальное для компьютера переопределение настроек проекта
try:
    from local_settings import *
except ImportError:
    pass

# When using Auto Escape you will notice that marking something as
# a Safestrings with Django will not affect the rendering in Jinja 2. To fix
# this you can monkeypatch Django to produce Jinja 2 compatible Safestrings:
from django.utils import safestring
if not hasattr(safestring, '__html__'):
    safestring.SafeString.__html__ = lambda self: str(self)
    safestring.SafeUnicode.__html__ = lambda self: unicode(self)
