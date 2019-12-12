"""
Создаём производные от форм UserChangeForm и UserCreationForm
из django.contrib.auth.forms. Переопределяем в них все методы
и классы, где используется модель User, заменяя её на CustomUser.

Если не создать таких производных, админка будет жаловаться,
что в формах нет новых полей, определённых в CustomUser.

"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import ugettext_lazy as _

from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username",)

    def clean_username(self):
        username = self.cleaned_data["username"]
        try:
            CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            return username
        raise forms.ValidationError(_("A user with that username already exists."))


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        exclude = ()
