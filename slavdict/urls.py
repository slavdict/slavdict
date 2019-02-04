# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import TemplateView

from slavdict.dictionary.admin import ui
admin.autodiscover()

urlpatterns = [
    url( r'^',           include('slavdict.dictionary.urls') ),
    url( r'^admin/',     include(admin.site.urls) ),
    url( r'^admin/doc/', include('django.contrib.admindocs.urls') ),
    url( r'^ui/',        include(ui.urls) ),
    url( r'^login/$',    LoginView.as_view() ),
    url( r'^logout/$',   LogoutView.as_view(next_page='/'), name='logout' ),
    url( r'^test/$',     TemplateView.as_view(template_name='test.html') ),
]

urlpatterns += staticfiles_urlpatterns()
