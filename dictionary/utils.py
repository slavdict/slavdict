# -*- coding: utf-8 -*-
from collections import defaultdict

from django.template import RequestContext

from coffin.shortcuts import render_to_response

from .models import Etymology
from .models import GreekEquivalentForExample
from .models import GreekEquivalentForMeaning

def non_unicode_greek(request):
    corrupted = 'corrupted' in request.GET

    greek_etymons = Etymology.objects.filter(language__slug='greek', corrupted=corrupted)
    greqex = GreekEquivalentForExample.objects.filter(corrupted=corrupted)
    greqm = GreekEquivalentForMeaning.objects.filter(corrupted=corrupted)

    words = [(i.text, i.host_entry.id, False, False) for i in greek_etymons if i.text]
    words.extend([(i.text, i.host_entry.id, False, i.for_example.id) for i in greqex if i.text])
    words.extend([(i.text, i.host_entry.id, i.for_meaning.id, False) for i in greqm if i.text])

    chardict = defaultdict(set)
    for word, entry_id, meaning_id, example_id in words:
        for char in word:
            chardict[char].add((word, entry_id, meaning_id, example_id))
    chars = sorted(chardict.keys())
    context = {
        'title': u'Неюникодные греческие символы',
        'chars': chars,
        'words': chardict,
    }
    return render_to_response('non_unicode_greek.html', context, RequestContext(request))
