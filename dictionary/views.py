# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext
from slavdict.dictionary.models import Entry

def all_entries(request):

    entries = Entry.objects.all()

    return render_to_response(

                'template1.django.html',

                { 'entries': entries, },

                RequestContext(request),

                )
