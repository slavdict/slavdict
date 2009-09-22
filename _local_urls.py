# Rename this file to local_urls.py 
# and use it if you want to add 
# the url for media files (css, js, images, ...) 
# for testing django without Apache web server
# in the current test site repository
# while still not having this url for the
# working site repository with Apache support.
# File local_urls.py will be ignored
# by current git repository.

from django.conf.urls.defaults import *

try:
    from settings import MEDIA_ROOT
except ImportError:
    MEDIA_ROOT = ''

urlpatterns = patterns('',
        url(
            r'^site-media/(?P<path>.*)$', 
            'django.views.static.serve', 
            {'document_root': MEDIA_ROOT}
        ),
    )
