# -*- coding: UTF-8 -*-
from django.forms import ModelForm, HiddenInput
from django.forms.models import inlineformset_factory

from dictionary.models import Entry, Meaning, Example, \
    Etymology, MeaningContext, GreekEquivalentForMeaning, \
    GreekEquivalentForExample

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

class EtymologyForm(ModelForm):
    class Meta:
        model = Etymology
        widgets = {
            'entry': HiddenInput,
            'collocation': HiddenInput,
            'order': HiddenInput,
        }

class MnngCntxtForm(ModelForm):
    class Meta:
        model = MeaningContext
        widgets = {
            'meaning': HiddenInput,
            'order': HiddenInput,
        }

class GrEqForMnngForm(ModelForm):
    class Meta:
        model = GreekEquivalentForMeaning
        widgets = {
            'for_meaning': HiddenInput,
        }

class GrEqForExForm(ModelForm):
    class Meta:
        model = GreekEquivalentForExample
        widgets = {
            'for_example': HiddenInput,
        }


from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

class RawValueWidget(Widget):
    def render(self, name, value, attrs=None):
        if value is None:
            value = u''
        return mark_safe(unicode(value))
