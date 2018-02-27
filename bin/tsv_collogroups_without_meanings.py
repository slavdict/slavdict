# coding: utf-8
from slavdict.dictionary.models import civilrus_convert
from slavdict.dictionary.models import CollocationGroup

LETTER = u'в'
OUTPUT_FILENAME = '/root/collogroups_without_meanings.tsv'

register = []
for cg in CollocationGroup.objects.all():
    if cg.host_entry.civil_equivalent.lower().startswith(LETTER):
        if not cg.all_meanings or all(
                not m.meaning.strip() and not m.gloss.strip()
                for m in cg.all_meanings):
            entry = cg.host_entry
            author = entry.authors.first().last_name
            register.append((author, entry, cg))

def sort_key(x):
    a, entry, cg = x
    e = (entry.civil_equivalent, entry.homonym_order)
    c = u'; '.join(c.collocation for c in cg.collocations)
    c = civilrus_convert(c)
    return a, e, c

register.sort(key=sort_key)

with open(OUTPUT_FILENAME, 'w') as f:
    f.write(u'Автор\tСтатья\tСловосочетание\n'.encode('utf-8'))
    for (a, entry, collogroup) in register:
        e = u'{0}{1} {2}'.format(entry.civil_equivalent,
                {1: u'¹', 2: u'²', 3: u'³'}.get(entry.homonym_order, u''),
                entry.get_part_of_speech_display())
        cg = u'; '.join(c.collocation for c in collogroup.collocations)
        f.write(u'{0}\t{1}\t{2}\n'.format(a, e, cg).encode('utf-8'))
