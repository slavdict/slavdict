import re

from slavdict.dictionary.models import Entry

LETTER = 'в'
FILENAME = '/root/vedi-wordforms.tsv'

RE = re.compile(r'[,;\s]+')
wordforms = []

for e in Entry.objects.all():
    if e.civil_equivalent.lower().startswith(LETTER):
        forms = []
        forms.append(('', [ov.idem for ov in e.orth_vars.all()]))
        if e.genitive.strip():
            forms.append(('Р.', RE.split(e.genitive.strip())))
        if e.short_form.strip():
            forms.append(('', RE.split(e.short_form.strip())))
        if e.nom_pl.strip():
            forms.append(('И. мн.', RE.split(e.nom_pl.strip())))
        if e.sg1.strip():
            forms.append(('', RE.split(e.sg1.strip())))
        if e.sg2.strip():
            forms.append(('', RE.split(e.sg2.strip())))
        if e.participles:
            forms.append(('', [p.idem for p in e.participles]))
        record = (e, forms)
        wordforms.append(record)

wordforms.sort(key=lambda x: (x[0].civil_inverse, x[0].homonym_order))

with open(FILENAME, 'w') as f:
    f.write('Лексема\tЧасть речи\tСловоформы\n')
    for (entry, forms) in wordforms:
        headword = entry.civil_equivalent
        pos = entry.get_part_of_speech_display()
        ho = {1: '¹', 2: '²', 3: '³'}.get(entry.homonym_order, '')
        hg = entry.homonym_gloss or ''
        template = '{0}{1} ‘{2}’' if hg else '{0}{1}'
        x = template.format(pos, ho, hg)
        forms0 = []
        for tag, forms1 in forms:
            forms2 = ''
            if tag:
                forms2 += '%s: ' % tag
            forms2 += ', '.join(forms1)
            forms0.append(forms2)
        frms = '; '.join(forms0)
        f.write('{0}\t{1}\t{2}\n'.format(headword, x, frms))
