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
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

MIDDLEWARE_CLASSES = (
#    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'slavdict.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    ROOT + 'templates/',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.static',
    'django.contrib.auth.context_processors.auth',
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

    'slavdict.dictionary',
    'slavdict.directory',

    'slavdict.custom_user',
    'slavdict.django_template_spaces',
    'slavdict.comments',

    'south',
#    'debug_toolbar',
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

# debug_toolbar
#DEBUG_TOOLBAR_PANELS = (
#    'debug_toolbar.panels.version.VersionDebugPanel',
#    'debug_toolbar.panels.timer.TimerDebugPanel',
#    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
#    'debug_toolbar.panels.headers.HeaderDebugPanel',
#    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
#    'debug_toolbar.panels.template.TemplateDebugPanel',
#    'debug_toolbar.panels.sql.SQLDebugPanel',
#    'debug_toolbar.panels.signals.SignalDebugPanel',
#    'debug_toolbar.panels.logger.LoggingPanel',
#)
#def custom_show_toolbar(request):
#    return True # Always show toolbar, for example purposes only.
#
#DEBUG_TOOLBAR_CONFIG = {
#    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
#    'HIDE_DJANGO_SQL': False,
#}


# Локальное для компьютера переопределение настроек проекта
try:
    from local_settings import *
except ImportError:
    pass
