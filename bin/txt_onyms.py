# coding: utf-8
from slavdict.dictionary.models import Entry

VOLUME = 2

onyms = []
onyms_others = []
others = []
for e in Entry.objects.all():
    if e.volume(VOLUME):
        if e.onym:
            # Отбираем имена собственные и топонимы
            if e.onym in (u'a', u'b'):
                onyms.append(e)
            else:
                onyms_others.append(e)
        else:
            others.append(e)

def sort_key(e):
    return e.civil_equivalent, e.homonym_order

onyms.sort(key=sort_key)
onyms_others.sort(key=sort_key)
others.sort(key=sort_key)

for name, entries in (('onyms', onyms), ('onyms_others', onyms_others)):
    with open('/root/%s.txt' % name, 'w') as f:
        for e in entries:
            order = {1: u'¹', 2: u'²', 3: u'³'}.get(e.homonym_order, u'')
            gloss = u' ‘{0}’'.format(e.homonym_gloss) if e.homonym_gloss else u''
            f.write(u'{0}{1}{2}\n'
                        .format(e.civil_equivalent, order, gloss)
                        .encode('utf-8'))

with open('/root/not_onyms.txt', 'w') as f:
    for e in others:
        if e.homonym_gloss:
            pattern = u'{0} {1} ‘{2}’'
        else:
            pattern = u'{0} {1}'
        order = {1: u'¹', 2: u'²', 3: u'³'}.get(e.homonym_order, u'')
        pos = e.get_part_of_speech_display()
        tag = pattern.format(order, pos, e.homonym_gloss)
        f.write(u'{0}{1}\t\n'
                    .format(e.civil_equivalent, tag)
                    .encode('utf-8'))
