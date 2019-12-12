from slavdict.dictionary.models import civilrus_convert
from slavdict.dictionary.models import CollocationGroup

LETTER = 'в'
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
    c = '; '.join(c.collocation for c in cg.collocations)
    c = civilrus_convert(c)
    return a, e, c

register.sort(key=sort_key)

with open(OUTPUT_FILENAME, 'w') as f:
    f.write('Автор\tСтатья\tСловосочетание\n')
    for (a, entry, collogroup) in register:
        e = '{0}{1} {2}'.format(entry.civil_equivalent,
                {1: '¹', 2: '²', 3: '³'}.get(entry.homonym_order, ''),
                entry.get_part_of_speech_display())
        cg = '; '.join(c.collocation for c in collogroup.collocations)
        f.write('{0}\t{1}\t{2}\n'.format(a, e, cg))
