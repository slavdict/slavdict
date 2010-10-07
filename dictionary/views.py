# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from slavdict.dictionary.models import Entry

def all_entries(request):
    entries = Entry.objects.all().order_by('civil_equivalent')
    return render_to_response('all_entries.html',
                            { 'entries': entries, 'title': u'Все статьи' },
                            RequestContext(request),)

def single_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    return render_to_response('single_entry.html',
                            { 'entry': entry, 'title': u'Статья «%s»' % entry.civil_equivalent },
                            RequestContext(request),)

def last_entry(request):
    entry = Entry.objects.all().order_by('-id')[0]
    return render_to_response('single_entry.html',
                            { 'entry': entry, 'title': u'Последняя добавленная статья' },
                            RequestContext(request),)
