# -*- coding: UTF-8 -*-
"""
Django settings for slavdict project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import pry
import __builtin__

# Базовые настройки проекта,
# от которых могут зависеть другие настройки
DEBUG = True

# Настройки, зависящие от базовых
# либо от которых не зависят другие настройки.
TEMPLATE_DEBUG = DEBUG

SERVER_EMAIL = 'no-reply@127.0.0.1'

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     __builtin__.DJANGO_ROOT + '.test.db',
    }
}

######################################
##  Настройки отдельных приложений  ##
######################################

# Сторонние библиотеки JavaScript
JSLIBS_SOURCE = {
    'jquery':            'http://cdnjs.cloudflare.com/ajax/libs/'
                         'jquery/2.1.1/jquery.js',
    'jquery_map':        'http://cdnjs.cloudflare.com/ajax/libs/'
                         'jquery/2.1.1/jquery.min.map',
    'jqueryUi':          'http://cdnjs.cloudflare.com/ajax/libs/'
                         'jqueryui/1.10.4/jquery-ui.js',
    'knockout':          'http://knockoutjs.com/downloads/knockout-3.2.0.debug.js',
    'knockoutMapping':   'https://raw.githubusercontent.com/SteveSanderson/'
                         'knockout.mapping/2.4.1/build/output/'
                         'knockout.mapping-latest.debug.js',
    'knockoutSortable':  'https://rawgit.com/rniemeyer/'
                         'knockout-sortable/v0.9.2/build/knockout-sortable.js',
    'knockoutPostbox':   'https://raw.githubusercontent.com/rniemeyer/'
                         'knockout-postbox/v0.4.2/build/knockout-postbox.js',
    'zeroClipboard':     'https://rawgit.com/zeroclipboard/'
                         'ZeroClipboard/v1.1.7/ZeroClipboard.js',
    'zeroClipboard_swf': 'https://raw.githubusercontent.com/zeroclipboard/'
                         'ZeroClipboard/v1.1.7/ZeroClipboard.swf',
    'opentip':           'https://rawgit.com/enyo/opentip/'
                         'v2.4.6/downloads/opentip-jquery.js',
    'opentipExCanvas':   'https://rawgit.com/enyo/opentip/'
                         'v2.4.6/downloads/opentip-jquery-excanvas.js',
}

