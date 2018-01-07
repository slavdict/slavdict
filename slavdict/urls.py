# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import LoginView, LogoutView

from slavdict.admin import ui
admin.autodiscover()

LOGIN_URL = 'login/'
urlpatterns = [
    url( r'^',          include('slavdict.dictionary.urls') ),
    url( r'^admin/',     include(admin.site.urls) ),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls') ),
    url( r'^ui/',        include(ui.urls) ),
    url( r'^%s$' % LOGIN_URL,    LoginView.as_view() ),
    url( r'^logout/$',   LogoutView.as_view(next_page=LOGIN_URL) ),
]

urlpatterns += staticfiles_urlpatterns()
