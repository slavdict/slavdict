# coding: utf-8
import sys

from slavdict.dictionary.models import *

hmap = {
    1: u'\u00b9',
    2: u'\u00b2',
    3: u'\u00b3',
    4: u'\u2074',
    None: u'',
}

def meanings(x):
    text = u''
    for m in x.meanings:
        text += u'%s. %s%s%s\n' % (m.order, u'ПЕРЕН. ' if m.figurative else u'', m.meaning,
                                   u' [%s]' % m.gloss if m.gloss else u'')
        for mm in m.child_meanings:
            text += u'   - %s%s%s%s\n' % (u'▶ ' if mm.metaphorical else u'',
                                          u'ПЕРЕН. ' if mm.figurative else u'', mm.meaning,
                                          u' [%s]' % mm.gloss if mm.gloss else u'')
    for m in x.metaph_meanings:
        text += u'▶  %s%s%s\n' % (u'ПЕРЕН. ' if m.figurative else u'', m.meaning,
                                  u' [%s]' % m.gloss if m.gloss else u'')
        for mm in m.child_meanings:
            text += u'   - %s%s%s%s\n' % (u'▶ ' if mm.metaphorical else u'',
                                          u'ПЕРЕН. ' if mm.figurative else u'', mm.meaning,
                                          u' [%s]' % mm.gloss if mm.gloss else u'')
    return text

es, cgs = [], []
for meaning in Meaning.objects.all():
    if meaning.figurative:
        if type(meaning.host) is Entry:
            es.append(meaning.host)
        elif type(meaning.host) is CollocationGroup:
            cgs.append(meaning.host)

f = open('figurative_meanings_4entries.txt', 'w')
for e in es:
    text = u'%s%s %s\n' % (e.civil_equivalent, hmap[e.homonym_order], e.get_part_of_speech_display())
    text += meanings(e) + u'\n'
    f.write(text.encode('utf-8'))
f.close()

f = open('figurative_meanings_4cg.txt', 'w')
for cg in cgs:
    text = u', '.join(c.collocation for c in cg.collocations) + u'\n'
    text += meanings(cg) + u'\n'
    f.write(text.encode('utf-8'))
f.close()
