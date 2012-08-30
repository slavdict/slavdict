# -*- coding: utf-8 -*-
from collections import defaultdict

from django.template import RequestContext

from coffin.shortcuts import render_to_response

from .models import Etymology
from .models import GreekEquivalentForExample
from .models import GreekEquivalentForMeaning

def non_unicode_greek(request):
    greek_etymons = Etymology.objects.filter(language__slug='greek')
    greqex = GreekEquivalentForExample.objects.all()
    greqm = GreekEquivalentForMeaning.objects.all()

    words = [i.text for i in greek_etymons if i.text]
    words.extend([i.text for i in greqex if i.text])
    words.extend([i.text for i in greqm if i.text])

    chardict = defaultdict(set)
    for word in words:
        for char in word:
            chardict[char].add(word)
    chars = sorted(chardict.keys())
    context = {
        'title': u'Неюникодные греческие символы',
        'chars': chars,
        'words': chardict,
    }
    return render_to_response('non_unicode_greek.html', context, RequestContext(request))
