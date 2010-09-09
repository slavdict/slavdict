# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from slavdict.custom_user.models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', '__unicode__',
                    'is_staff', 'is_active')
    fieldsets = (
        (None, {
            'fields': (
                'username',
                'password',
                ),
            }),
        (u'персональная инормация', {
            'fields': (
                # second_name -- добавленное в CustomUser поле.
                ('last_name', 'first_name', 'second_name'),
                'email',
                ),
            }),
        (u'права', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'user_permissions',
                ),
            }),
        (u'важные даты', {
            'fields': (
                'last_login',
                'date_joined',
                ),
            }),
        (u'группы', {
            'fields': (
                'groups',
                ),
            }),
        )

admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)
