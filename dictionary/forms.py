# -*- coding: UTF-8 -*-
from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from dictionary.models import Entry, Meaning, Example

class EntryForm(ModelForm):
    class Meta:
        model = Entry
