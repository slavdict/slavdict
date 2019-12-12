from slavdict.dictionary.models import *

hmap = {
    1: '\u00b9',
    2: '\u00b2',
    3: '\u00b3',
    4: '\u2074',
    None: '',
}

def meanings(x):
    text = ''
    for m in x.meanings:
        text += '%s. %s%s%s\n' % (m.order, 'ПЕРЕН. ' if m.figurative else '',
                m.meaning, ' [%s]' % m.gloss if m.gloss else '')
        for mm in m.child_meanings:
            text += '   - %s%s%s%s\n' % ('▶ ' if mm.metaphorical else '',
                    'ПЕРЕН. ' if mm.figurative else '', mm.meaning, ' [%s]'
                    % mm.gloss if mm.gloss else '')
    for m in x.metaph_meanings:
        text += '▶  %s%s%s\n' % ('ПЕРЕН. ' if m.figurative else '', m.meaning,
                ' [%s]' % m.gloss if m.gloss else '')
        for mm in m.child_meanings:
            text += '   - %s%s%s%s\n' % ('▶ ' if mm.metaphorical else '',
                    'ПЕРЕН. ' if mm.figurative else '', mm.meaning, ' [%s]'
                    % mm.gloss if mm.gloss else '')
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
    text = '%s%s %s\n' % (e.civil_equivalent.upper(),
            hmap[e.homonym_order], e.get_part_of_speech_display())
    text += meanings(e) + '\n'
    f.write(text)
f.close()

f = open('liturgsymb4collocations.txt', 'w')
for cg in sorted(cgs, key=lambda x: x.host_entry.civil_equivalent):
    text = ', '.join(c.collocation.upper() for c in cg.collocations) + '\n'
    text += meanings(cg) + '\n'
    f.write(text)
f.close()
