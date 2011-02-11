# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import RequestContext
from slavdict.dictionary.models import Entry, \
    Meaning, Example, OrthographicVariant, Etymology
import datetime

def all_entries(request):
    entries = Entry.objects.all().order_by('civil_equivalent', 'homonym_order')
    return render_to_response('all_entries.html',
                            { 'entries': entries,
                              'title': u'Все статьи',
                              'show_additional_info': 'ai' in request.COOKIES,
                              'user': request.user },
                            RequestContext(request),)

def single_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    return render_to_response('single_entry.html',
                            { 'entry': entry,
                              'title': u'Статья «%s»' % entry.civil_equivalent,
                              'show_additional_info': 'ai' in request.COOKIES,
                              'user': request.user },
                            RequestContext(request),)

def last_entry(request):
    error = False
    try:
        entry = Entry.objects.all().order_by('-id')[0]
    except IndexError:
        entry = None
        error = True
    return render_to_response('single_entry.html',
                            { 'entry': entry,
                              'title': u'Последняя добавленная статья',
                              'show_additional_info': 'ai' in request.COOKIES,
                              'error': error,
                              'user': request.user },
                            RequestContext(request),)

def switch_additional_info(request):
    referer = request.META.get('HTTP_REFERER', '/')
    response = redirect(referer)
    if 'ai' in request.COOKIES:
        response.delete_cookie('ai')
    else:
        date_expired = datetime.datetime.now() + datetime.timedelta(days=90)
        response.set_cookie('ai', max_age=7776000, expires=date_expired)
    return response



from django.forms.models import modelformset_factory
from slavdict.dictionary.forms import EntryForm

def change_entry(request, entry_id):

    entry = Entry.objects.get(pk=entry_id)

    # Орфографические варианты.
    orth_vars = entry.orth_vars

    # Значения данной словарной статьи.
    meanings = Meaning.objects.filter(entry_container=entry)
    l = range(len(meanings))

    # Список, содержащий в качестве элементов группы примеров,
    # относящиеся к одному значению.
    example_groups = [Example.objects.filter(meaning=m) for m in meanings]

    MeaningFormSet = modelformset_factory(Meaning)
    ExampleFormSet = modelformset_factory(Example)
    OrthVarFormSet = modelformset_factory(OrthographicVariant)

    if request.method == "POST":
        entry_form = EntryForm(request.POST, instance=entry)
        meaning_formset = MeaningFormSet(request.POST,
            queryset=meanings, prefix='meaning')
        example_formset_groups = [ExampleFormSet(request.POST, queryset=eg) for eg in example_groups]
        orth_var_formset = OrthVarFormSet(request.POST, queryset=orth_vars, prefix='orthvar')
    else:
        entry_form = EntryForm(instance=entry)
        meaning_formset = MeaningFormSet(queryset=meanings, prefix='meaning')
        example_formset_groups = [ExampleFormSet(queryset=eg) for eg in example_groups]
        orth_var_formset = OrthVarFormSet(queryset=orth_vars, prefix='orthvar')

    meaning_formset.with_examples = [(meaning_formset.forms[i], example_formset_groups[i]) for i in l]

    return render_to_response("change_form.html", {
        'entry_form': entry_form,
        'meaning_formset': meaning_formset,
        'orth_var_formset': orth_var_formset,
    })
