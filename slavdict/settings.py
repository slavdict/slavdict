# -*- coding: UTF-8 -*-
"""
Django settings for slavdict project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
from os.path import abspath
from os.path import dirname
from os.path import normpath
import sys

# Базовые настройки проекта,
# от которых могут зависеть другие настройки
DEBUG = False
ROOT = normpath(abspath(dirname(dirname(__file__)))).replace('\\', '/') + '/'

# Локальное переопределение базовых настроек,
# если оно имеется.
try:
    from local_base_settings import *
except ImportError:
    pass

# Настройки, зависящие от базовых
# либо от которых не зависят другие настройки.
TEMPLATE_DEBUG = DEBUG

ADMINS = ()
MANAGERS = ADMINS
BACKUP_MANAGERS = MANAGERS
BACKUP_DIR = ROOT + '.dumps/'

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
USE_TZ = False

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru'

USE_I18N = True
USE_L10N = True

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
STATIC_RESOURCES_VERSION='2016.08.29-12.09'

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
    'slavdict.middleware.ValidCookieMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
   #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'slavdict.urls'

WSGI_APPLICATION = 'slavdict.wsgi.application'

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
    'slavdict.context_processors.staticfiles',
)

STATICFILES_DIRS = (
    ROOT + 'static/',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'coffin',

    'slavdict.dictionary',
    'slavdict.custom_user',
    'slavdict.django_template_spaces',
)

######################################
##  Настройки отдельных приложений  ##
######################################

# custom_user
AUTHENTICATION_BACKENDS = (
    'slavdict.auth_backends.CustomUserModelBackend',
    'django.contrib.auth.backends.ModelBackend',
)
CUSTOM_USER_MODEL = 'slavdict.custom_user.CustomUser'

# Сторонние библиотеки JavaScript
JSLIBS_VERSION = '2014.10.31'
JSLIBS_URL = STATIC_URL + 'js/outsourcing/'
JSLIBS_PATH = ROOT + 'static/js/outsourcing/'
JSLIBS = {
    'jquery': {
      'debug': '//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.js',
        'min': '//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.js',
        'map': '//cdnjs.cloudflare.com/ajax/libs/jquery/2.1.1/jquery.min.map',
    },
    'jqueryUi': {
      'debug': '//cdnjs.cloudflare.com/ajax/libs/jqueryui/1.10.4/jquery-ui.js',
        'min': '//cdnjs.cloudflare.com/ajax/libs/'
               'jqueryui/1.10.4/jquery-ui.min.js',
    },
    'knockout': {
        'debug': 'http://knockoutjs.com/downloads/knockout-3.2.0.debug.js',
        'min': '//cdnjs.cloudflare.com/ajax/libs/'
               'knockout/3.2.0/knockout-min.js',
    },
    'knockoutMapping': {
        'debug': 'https://raw.githubusercontent.com/SteveSanderson/'
                 'knockout.mapping/2.4.1/build/output/'
                 'knockout.mapping-latest.debug.js',
         'Xmin': 'https://raw.githubusercontent.com/SteveSanderson/'
                 'knockout.mapping/2.4.1/build/output/'
                 'knockout.mapping-latest.js',
    },
    'knockoutSortable': {
        'debug': 'https://rawgit.com/rniemeyer/'
                 'knockout-sortable/v0.9.2/build/knockout-sortable.js',
         'Xmin': 'https://raw.githubusercontent.com/rniemeyer/'
                 'knockout-sortable/v0.9.2/build/knockout-sortable.min.js',
        # NOTE: Файлы с raw.githubusercontent.com нельзя отдавать в продакшн.
        # Там выставляются http-заголовки
        #
        #   Content-Type: text/plain; charset=utf-8
        #   X-Content-Type-Options: nosniff
        #
        # что запрещает браузеру распознавать js-файл как js-файл.
        # Домен rawgit.com специально предназначен в помощь разработчикам для
        # обхода этой проблемы, но расчитан исключительно для тестирования,
        # отладки, демонстрации. При нагрузке его трафиком соединения будут
        # скидываться. См. http://rawgit.com/
        #
        # Ключ ``Xmin`` вместо ``min`` использован специально, чтобы этот адрес
        # не отдавался в продакшн.
    },
    'knockoutPostbox': {
        'debug': 'https://raw.githubusercontent.com/rniemeyer/'
                 'knockout-postbox/v0.4.2/build/knockout-postbox.js',
         'Xmin': 'https://raw.githubusercontent.com/rniemeyer/'
                 'knockout-postbox/v0.4.2/build/knockout-postbox.min.js',
    },
    'zeroClipboard': {
        'debug': 'https://rawgit.com/zeroclipboard/'
                 'ZeroClipboard/v1.1.7/ZeroClipboard.js',
         'Xmin': 'https://raw.githubusercontent.com/zeroclipboard/'
                 'ZeroClipboard/v1.1.7/ZeroClipboard.min.js',
          'swf': 'https://raw.githubusercontent.com/zeroclipboard/'
                 'ZeroClipboard/v1.1.7/ZeroClipboard.swf',
    },
    'opentip': {
        'debug': 'https://rawgit.com/enyo/opentip/'
                 'v2.4.6/downloads/opentip-jquery.js',
         'Xmin': 'https://raw.githubusercontent.com/enyo/opentip/'
                 'v2.4.6/downloads/opentip-jquery.min.js',
    },
    'opentipExCanvas': {
        'debug': 'https://rawgit.com/enyo/opentip/'
                 'v2.4.6/downloads/opentip-jquery-excanvas.js',
         'Xmin': 'https://raw.githubusercontent.com/enyo/opentip/'
                 'v2.4.6/downloads/opentip-jquery-excanvas.min.js',
    },
}

_postfix = 'Local'
for lib in JSLIBS:
    for version in JSLIBS[lib].keys():
        filename = JSLIBS[lib][version].split('/')[-1].split('?')[0]
        if version == 'Xmin':
            JSLIBS[lib]['min'] = JSLIBS_URL + filename
            version = 'min'
        JSLIBS[lib][version + _postfix] = JSLIBS_URL + filename + '?' + STATIC_RESOURCES_VERSION


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


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '--jslibs':
            """ Использование аргумента --jslibs

            Данный вывод в stdout используется в цели jslibs из Makefile.
            Вывод имеет следующий вид:

              [<ссылка на файл в интернете> -O <абс. имя файла в локальной ФС>]*

            Каждая такая тройка предназначена для wget. Он её будет получать
            следующим образом:

              python settings.py --jslibs | xargs -n3 wget

            От второго элемента тройки ("-O") отказаться не получилось, т.к.
            аргументы xargs -L или -n и -I не совместимы (см. man xargs /BUGS).
            Иначе можно было бы вместо троек использовать двойки и писать:

              python settings.py --jslibs | xargs -n2 -I{} wget {} -O {}

            """
            xargs_wget = []
            for lib in JSLIBS:
                for version in [k
                                for k in JSLIBS[lib]
                                if not k.endswith(_postfix)]:
                    url = JSLIBS[lib][version]
                    if url.startswith('//'):
                        url = 'http:' + url
                    elif not url.startswith('http'):
                        continue
                    xargs_wget.append(url)
                    xargs_wget.append('-O')
                    xargs_wget.append(JSLIBS_PATH + url.split('/')[-1])
            sys.stdout.write(' '.join(xargs_wget))

        elif sys.argv[1] == '--jslibs-path':
            sys.stdout.write(JSLIBS_PATH)

        elif sys.argv[1] == '--jslibs-version':
            sys.stdout.write(JSLIBS_VERSION)
