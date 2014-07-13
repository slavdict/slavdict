# -*- coding: UTF-8 -*-
# Django settings for slavdict project.
import os
import sys

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
TIME_ZONE = 'Etc/GMT-4'
USE_TZ = False

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
STATIC_RESOURCES_VERSION='2014.07.13'

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
    'slavdict.context_processors.staticfiles',
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

# Сторонние библиотеки JavaScript
JSLIBS_VERSION = '2013.09.24'
JSLIBS_URL = STATIC_URL + 'js/outsourcing/'
JSLIBS_PATH = ROOT + 'static/js/outsourcing/'
JSLIBS = {
    'jquery': {
        'debug': '//cdnjs.cloudflare.com/ajax/libs/jquery/2.0.2/jquery.js',
        'min': '//cdnjs.cloudflare.com/ajax/libs/jquery/2.0.2/jquery.min.js',
        'map': '//cdnjs.cloudflare.com/ajax/libs/jquery/2.0.2/jquery.min.map',
    },
    'jqueryUi': {
        'debug': '//cdnjs.cloudflare.com/ajax/libs/jqueryui/1.10.3/jquery-ui.js',
        'min': '//cdnjs.cloudflare.com/ajax/libs/jqueryui/1.10.3/jquery-ui.min.js',
    },
    'knockout': {
        'debug': 'http://knockoutjs.com/downloads/knockout-2.3.0.debug.js',
        'min': '//cdnjs.cloudflare.com/ajax/libs/knockout/2.3.0/knockout-min.js',
    },
    'knockoutMapping': {
        'debug': '//cdnjs.cloudflare.com/ajax/libs/knockout.mapping/2.3.5/knockout.mapping.js',
        'min': '//cdnjs.cloudflare.com/ajax/libs/knockout.mapping/2.3.5/knockout.mapping.min.js',
    },
    'knockoutSortable': {
        'debug': 'https://rawgithub.com/rniemeyer/knockout-sortable/v0.8.2/build/knockout-sortable.js',
        'Xmin': 'https://raw.github.com/rniemeyer/knockout-sortable/v0.8.2/build/knockout-sortable.min.js',
        # NOTE: Файлы с raw.github.com нельзя отдавать в продакшн. Там
        # выставляются http-заголовки
        #
        #   Content-Type: text/plain; charset=utf-8
        #   X-Content-Type-Options: nosniff
        #
        # что запрещает браузеру распознавать js-файл как js-файл.
        # Домен rawgithub.com (после raw нету точки!) специально предназначен
        # в помощь разработчикам для обхода этой проблемы, но расчитан
        # исключительно для тестирования, отладки, демонстрации. При нагрузке
        # его трафиком соединения будут скидываться. См. http://rawgithub.com/
        #
        # Ключ ``Xmin`` вместо ``min`` использован специально, чтобы этот адрес
        # не отдавался в продакшн.
    },
    'knockoutPostbox': {
        'debug': 'https://rawgithub.com/rniemeyer/knockout-postbox/v0.3.1/build/knockout-postbox.js',
        'Xmin': 'https://raw.github.com/rniemeyer/knockout-postbox/v0.3.1/build/knockout-postbox.min.js',
    },
    'zeroClipboard': {
        'debug': 'https://rawgithub.com/zeroclipboard/ZeroClipboard/v1.1.7/ZeroClipboard.js',
        'Xmin': 'https://raw.github.com/zeroclipboard/ZeroClipboard/v1.1.7/ZeroClipboard.min.js',
        'swf': 'https://github.com/zeroclipboard/ZeroClipboard/raw/v1.1.7/ZeroClipboard.swf',
    },
    'opentip': {
        'debug': 'https://rawgithub.com/enyo/opentip/v2.4.6/downloads/opentip-jquery.js',
        'Xmin': 'https://raw.github.com/enyo/opentip/v2.4.6/downloads/opentip-jquery.min.js',
    },
    'opentipExCanvas': {
        'debug': 'https://rawgithub.com/enyo/opentip/v2.4.6/downloads/opentip-jquery-excanvas.js',
        'Xmin': 'https://raw.github.com/enyo/opentip/v2.4.6/downloads/opentip-jquery-excanvas.min.js',
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
