# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.template import RequestContext
from slavdict.dictionary.models import Entry, Meaning, Example
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



from django.forms.models import inlineformset_factory
from slavdict.dictionary.forms import EntryForm

def change_entry(request, entry_id):
    entry = Entry.objects.get(pk=entry_id)
    MeaningInlineFormSet = inlineformset_factory(Entry, Meaning, fk_name='entry_container')
    if request.method == "POST":
        formset = MeaningInlineFormSet(request.POST, request.FILES, instance=entry)
        if formset.is_valid():
            formset.save()
            # Do something.
    else:
        formset = MeaningInlineFormSet(instance=entry)
    return render_to_response("change_form.html", {
        "formset": formset,
    })
