from os.path import abspath
from os.path import dirname
from os.path import normpath
from os.path import exists
import sys
import json
import hashlib

# Базовые настройки проекта,
# от которых могут зависеть другие настройки
DEBUG = False
ROOT = normpath(abspath(dirname(dirname(__file__)))).replace('\\', '/') + '/'

# Локальное переопределение базовых настроек,
# если оно имеется.
try:
    from .local_base_settings import *
except ImportError:
    pass

# Настройки, зависящие от базовых
# либо от которых не зависят другие настройки.
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

_hash_file = ROOT + '.hash'
_default_hash = 'NOHASH'

if exists(_hash_file):
    try:
        STATIC_RESOURCES_VERSION = open(_hash_file).read().strip()
    except:
        print(_hash_file, 'could not be read')
        sys.exit(1)

MIDDLEWARE = (
    'slavdict.middleware.ValidCookieMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
)

ROOT_URLCONF = 'slavdict.urls'

WSGI_APPLICATION = 'slavdict.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.static',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [
            ROOT + 'templates/',
        ],
        'APP_DIRS': False,
        'OPTIONS': {
            'autoescape': False,
            'environment': 'slavdict.jinja2.environment',
            'extensions': [
                'jinja2.ext.do',
                'slavdict.jinja_extensions.trim_spaces.trim',
            ],
        },
    },
]

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

    'rangefilter',

    'slavdict.custom_user',
    'slavdict.dictionary',
    'slavdict.csl_annotations',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'slavdict': {
            '()': 'django.utils.log.ServerFormatter',
            'format': '[{server_time}] {message}',
            'style': '{',
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'formatter': 'slavdict',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django/slavdict.log',
        },
    },
    'loggers': {
        'slavdict': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    }
}

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
JSLIBS_URL = STATIC_URL + 'js/outsourcing/'
JSLIBS_PATH = ROOT + 'static/js/outsourcing/'
CDN = '//cdnjs.cloudflare.com/ajax/libs/'
JSLIBS = {
    'jquery': {
      'debug': CDN + 'jquery/3.5.1/jquery.js',
        'min': CDN + 'jquery/3.5.1/jquery.min.js',
        'map': CDN + 'jquery/3.5.1/jquery.min.map',
    },
    'jqueryUi': {
      'debug': CDN + 'jqueryui/1.12.1/jquery-ui.js',
        'min': CDN + 'jqueryui/1.12.1/jquery-ui.min.js',
        'css': CDN + 'jqueryui/1.12.1/jquery-ui.min.css',
    },
    'knockout': {
      'debug': CDN + 'knockout/3.5.1/knockout-latest.debug.js',
        'min': CDN + 'knockout/3.5.1/knockout-latest.min.js',
    },
    'knockoutSortable': {
      'debug': CDN + 'knockout-sortable/1.2.0/knockout-sortable.js',
        'min': CDN + 'knockout-sortable/1.2.0/knockout-sortable.min.js',
    },
    'knockoutPostbox': {
      'debug': CDN + 'knockout-postbox/0.6.0/knockout-postbox.js',
        'min': CDN + 'knockout-postbox/0.6.0/knockout-postbox.min.js',
    },
    'clipboardjs': {
      'debug': CDN + 'clipboard.js/1.7.1/clipboard.js',
        'min': CDN + 'clipboard.js/1.7.1/clipboard.min.js',
    },
    'opentip': {
      'debug': CDN + 'opentip/2.4.6/downloads/opentip-jquery.js',
        'min': CDN + 'opentip/2.4.6/downloads/opentip-jquery.min.js',
    },
    'fontAwesome': {
        'Xmin': 'http://use.fontawesome.com/releases/v5.0.7/js/all.js',
        # NOTE: Ключ ``Xmin`` вместо ``min`` использован специально,
        # чтобы этот адрес не отдавался в продакшн.
    },
}
JSLIBS_VERSION = hashlib.md5(json.dumps(JSLIBS).encode('utf-8')).hexdigest()[:8]

_postfix = 'Local'
for lib in JSLIBS:
    for version in list(JSLIBS[lib].keys()):
        filename = JSLIBS[lib][version].split('/')[-1].split('?')[0]
        if version == 'Xmin':
            JSLIBS[lib]['min'] = JSLIBS_URL + filename
            version = 'min'
        JSLIBS[lib][version + _postfix] = JSLIBS_URL + filename + '?' + JSLIBS_VERSION


# Локальное для компьютера переопределение настроек проекта
try:
    from .local_settings import *
except ImportError:
    pass

# Jinja2 compatible Safestrings
from django.utils import safestring
if not hasattr(safestring, '__html__'):
    safestring.SafeText.__html__ = lambda self: str(self)


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
