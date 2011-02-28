# -*- coding: UTF-8 -*-
from django.forms import ModelForm, \
    HiddenInput, TextInput
from django.forms.models import inlineformset_factory

from dictionary.models import Entry, Meaning, Example, \
    Etymology, MeaningContext, GreekEquivalentForMeaning, \
    GreekEquivalentForExample

class EntryForm(ModelForm):
    class Meta:
        model = Entry
        widgets = {
            'civil_equivalent': HiddenInput,
            'hidden': HiddenInput,
            'homonym_order': HiddenInput,
            'homonym_gloss': HiddenInput,
            'word_forms_list': HiddenInput,
            'transitivity': HiddenInput,

            'derivation_entry': HiddenInput,
            'link_to_entry': HiddenInput,
            'link_to_collogroup': HiddenInput,
            'link_to_meaning': HiddenInput,
            'cf_entries': HiddenInput,
            'cf_collogroups': HiddenInput,
            'cf_meanings': HiddenInput,

            'status': HiddenInput,
            'percent_status': HiddenInput,
            'editor': HiddenInput,
            'antconc_query': HiddenInput,
            'grequiv_status': HiddenInput,
        }

class MeaningForm(ModelForm):

    class Meta:
        model = Meaning
        widgets = {
            'entry_container': HiddenInput,
            'collogroup_container': HiddenInput,
            'order': HiddenInput,
            'parent_meaning': HiddenInput,
            'hidden': HiddenInput,

            'link_to_meaning': HiddenInput,
            'link_to_entry': HiddenInput,
            'link_to_collogroup': HiddenInput,
            'cf_entries': HiddenInput,
            'cf_collogroups': HiddenInput,
            'cf_meanings': HiddenInput,
        }

class ExampleForm(ModelForm):
    class Meta:
        model = Example
        widgets = {
            'meaning': HiddenInput,
            'order': HiddenInput,
            'hidden': HiddenInput,
        }

class OrthVarForm(ModelForm):
    class Meta:
        model = Example
        widgets = {
            'entry': HiddenInput,
            'order': HiddenInput,

            'idem': TextInput(attrs={'class':'x5 y1 antconsol'}),
        }

class EtymologyForm(ModelForm):
    class Meta:
        model = Etymology
        widgets = {
            'entry': HiddenInput,
            'collocation': HiddenInput,
            'order': HiddenInput,
            'etymon_to': HiddenInput,
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
            'position': HiddenInput,
        }


from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

class RawValueWidget(Widget):
    def render(self, name, value, attrs=None):
        if value is None:
            value = u''
        return mark_safe(unicode(value))
