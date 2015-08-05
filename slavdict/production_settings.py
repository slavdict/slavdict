# -*- coding: UTF-8 -*-
"""
Django settings for slavdict project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""
import __builtin__

# Базовые настройки проекта,
# от которых могут зависеть другие настройки
DEBUG = False

# Настройки, зависящие от базовых
# либо от которых не зависят другие настройки.
TEMPLATE_DEBUG = DEBUG

SERVER_EMAIL = 'no-reply@slavdict.ruslang.ru'

DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.sqlite3',
        'NAME':     __builtin__.DJANGO_ROOT + '.production.db',
    }
}

JSLIBS = {
    'jquery':            'http://cdnjs.cloudflare.com/ajax/libs/'
                         'jquery/2.1.1/jquery.min.js',
    'jquery_map':        'http://cdnjs.cloudflare.com/ajax/libs/'
                         'jquery/2.1.1/jquery.min.map',
    'jqueryUi':          'http://cdnjs.cloudflare.com/ajax/libs/'
                         'jqueryui/1.10.4/jquery-ui.min.js',
    'knockout':          'http://cdnjs.cloudflare.com/ajax/libs/'
                         'knockout/3.2.0/knockout-min.js',
    'knockoutMapping':   'https://raw.githubusercontent.com/SteveSanderson/'
                         'knockout.mapping/2.4.1/build/output/'
                         'knockout.mapping-latest.js',
    'knockoutSortable':  'https://raw.githubusercontent.com/rniemeyer/'
                         'knockout-sortable/v0.9.2/build/knockout-sortable.min.js',
    'knockoutPostbox':   'https://raw.githubusercontent.com/rniemeyer/'
                         'knockout-postbox/v0.4.2/build/knockout-postbox.min.js',
    'zeroClipboard':     'https://raw.githubusercontent.com/zeroclipboard/'
                         'ZeroClipboard/v1.1.7/ZeroClipboard.min.js',
    'zeroClipboard_swf': 'https://raw.githubusercontent.com/zeroclipboard/'
                         'ZeroClipboard/v1.1.7/ZeroClipboard.swf',
    'opentip':           'https://raw.githubusercontent.com/enyo/opentip/'
                         'v2.4.6/downloads/opentip-jquery.min.js',
    'opentipExCanvas':   'https://raw.githubusercontent.com/enyo/opentip/'
                         'v2.4.6/downloads/opentip-jquery-excanvas.min.js',
}

JSLIBS_LOCAL = ( 'knockoutMapping', 'knockoutSortable', 'knockoutPostbox',
                 'zeroClipboard', 'zeroClipboard_swf', 'opentip',
                 'opentipExCanvas' )
