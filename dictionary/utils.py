# -*- coding: utf-8 -*-
from collections import defaultdict

from django.template import RequestContext

from coffin.shortcuts import render_to_response

from .models import Etymology
from .models import GreekEquivalentForExample
from .models import GreekEquivalentForMeaning

def non_unicode_greek(request):
    corrupted = 'corrupted' in request.GET
    nowrap = 'nowrap' in request.GET

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
        'nowrap': nowrap,
    }
    return render_to_response('non_unicode_greek.html', context, RequestContext(request))


ULYSSESMAP = (
    (u'\u2026', u'...'),
    (u'\uf020', u' '),
    (u'\uf026', u'\u1fbd'), # koronis
    (u'\uf028', u'('),
    (u'\uf029', u')'),
    (u'\uf02c', u','),
    (u'\uf02d', u'-'),
    (u'\uf02e', u'.'),
    (u'\uf03c(.)', ur'\1\u0314'), # dasia
    (u'\uf03d', u'='),
    (u'\uf03e(.)', ur'\1\u0313'), # psili

    (u'\uf041', u'\u0391'), # Alpha
    (u'\uf042', u'\u0392'), # Beta
    (u'\uf044', u'\u0394'), # Delta
    (u'\uf045', u'\u0395'), # Epsilon
    (u'\uf047', u'\u0393'), # Gamma
    (u'\uf049', u'\u0399'), # Iota
    (u'\uf04a', u'\u0397'), # Eta
    (u'\uf04b', u'\u039a'), # Kappa
    (u'\uf04d', u'\u039c'), # Mu
    (u'\uf04e', u'\u039d'), # Nu
    (u'\uf04f', u'\u039f'), # Omicron
    (u'\uf050', u'\u03a0'), # Pi
    (u'\uf051', u'\u0398'), # Theta
    (u'\uf053', u'\u03a3'), # Sigma
    (u'\uf055', u'\u03a5'), # Upsilon
    (u'\uf05b', u'['),
    (u'\uf05d', u']'),
    (u'\uf061', u'\u03b1'), # alpha
    (u'\uf062', u'\u03b2'), # beta
    (u'\uf063', u'\u03c7'), # chi
    (u'\uf064', u'\u03b4'), # delta
    (u'\uf065', u'\u03b5'), # epsilon
    (u'\uf066', u'\u03c6'), # phi
    (u'\uf067', u'\u03b3'), # gamma
    (u'\uf069', u'\u03b9'), # iota
    (u'\uf06a', u'\u03b7'), # eta
    (u'\uf06b', u'\u03ba'), # kappa
    (u'\uf06c', u'\u03bb'), # lambda
    (u'\uf06d', u'\u03bc'), # mu
    (u'\uf06e', u'\u03bd'), # nu
    (u'\uf06f', u'\u03bf'), # omicron
    (u'\uf070', u'\u03c0'), # pi
    (u'\uf071', u'\u03b8'), # theta
    (u'\uf072', u'\u03c1'), # rho
    (u'\uf073', u'\u03c3'), # sigma
    (u'\uf074', u'\u03c4'), # tau
    (u'\uf075', u'\u03c5'), # upsilon
    (u'\uf076', u'\u03c2'), # sigma final
    (u'\uf077', u'\u03c9'), # omega
    (u'\uf078', u'\u03be'), # xi (ksi)
    (u'\uf079', u'\u03c8'), # psi
    (u'\uf07a', u'\u03b6'), # zeta

    (u'\uf080', u'\u1f71'), # alpha with oxia
    (u'\uf081', u'\u1f70'), # alpha with varia
    (u'\uf082', u'\u1fb6'), # alpha with perispomeni
    (u'\uf083', u'\u1f01'), # alpha with dasia
    (u'\uf084', u'\u1f05'), # alpha with dasia and oxia
    (u'\uf087', u'\u1f00'), # alpha with psili
    (u'\uf088', u'\u1f04'), # alpha with psili and oxia
    (u'\uf089', u'\u1f02'), # alpha with psili and varia
    (u'\uf08b', u'\u1fb3'), # alpha with ypogigrammeni
    (u'\uf090', u'\u1f85'), # alpha with dasia, oxia and ypogigrammeni

    (u'\uf099', u'\u1f73'), # epsilon with oxia
    (u'\uf09a', u'\u1f72'), # epsilon with varia
    (u'\uf09c', u'\u1f15'), # epsilon with dasia and oxia
    (u'\uf09d', u'\u1f10'), # epsilon with psili
    (u'\uf09e', u'\u1f14'), # epsilon with psili and oxia

    (u'\uf0a9(.)', ur'\1\u0314\u0301'), # dasia and oxia
    (u'\uf0ad(.)', ur'\1\u0313\u0300'), # psili and varia
    (u'\uf0af(.)', ur'\1\u0313\u0342'), # psili and perispomeni
)

def ulysses2unicode(text, mapping=ULYSSESMAP):
    for src, dst in mapping:
        text = text.replace(src, dst)
    return text
