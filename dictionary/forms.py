# -*- coding: UTF-8 -*-
from django.forms import ModelForm, HiddenInput
from django.forms.models import inlineformset_factory

from dictionary.models import Entry, Meaning, Example

class EntryForm(ModelForm):
    class Meta:
        model = Entry

class MeaningForm(ModelForm):

    class Meta:
        model = Meaning
        widgets = {
            'entry_container': HiddenInput,
            'collogroup_container': HiddenInput,
            'order': HiddenInput,
        }

class ExampleForm(ModelForm):
    class Meta:
        model = Example
        widgets = {
            'meaning': HiddenInput,
            'order': HiddenInput,
        }

class OrthVarForm(ModelForm):
    class Meta:
        model = Example
        widgets = {
            'entry': HiddenInput,
            'order': HiddenInput,
        }
