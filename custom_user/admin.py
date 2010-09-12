# -*- coding: utf-8 -*-
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from slavdict.custom_user.models import CustomUser
from slavdict.custom_user.forms import CustomUserChangeForm, CustomUserCreationForm

class CustomUserAdmin(UserAdmin):

    list_display = ('username', '__unicode__',
                    'is_staff', 'is_active')

    # Поле fildsets делаем как у UserAdmin.
    # Меняем там блок полей, озаглавленный Personal Info.
    # См. django.contrib.auth.admin.UserAdmin
    fieldsets = UserAdmin.fieldsets
    fieldsets[1][1]['fields'] = (
        ('last_name', 'first_name', 'second_name'),
        'email',
        )

    # В полях форм используем наши формы,
    # где используется модель CustomUser вместо User.
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm


admin.site.unregister(User)
admin.site.register(CustomUser, CustomUserAdmin)
