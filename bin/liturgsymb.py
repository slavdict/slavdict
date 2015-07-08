# coding: utf-8
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

es, cgs = set(), set()
for meaning in Meaning.objects.all():
    if meaning.metaphorical:
        if type(meaning.host) is Entry:
            es.add(meaning.host)
        elif type(meaning.host) is CollocationGroup:
            cgs.add(meaning.host)

f = open('liturgsymb4lexemes.txt', 'w')
for e in sorted(es, key=lambda x: x.civil_equivalent):
    text = u'%s%s %s\n' % (e.civil_equivalent.upper(),
            hmap[e.homonym_order], e.get_part_of_speech_display())
    text += meanings(e) + u'\n'
    f.write(text.encode('utf-8'))
f.close()

f = open('liturgsymb4collocations.txt', 'w')
for cg in sorted(cgs, key=lambda x: x.host_entry.civil_equivalent):
    text = u', '.join(c.collocation.upper() for c in cg.collocations) + u'\n'
    text += meanings(cg) + u'\n'
    f.write(text.encode('utf-8'))
f.close()
