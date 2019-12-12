from slavdict.dictionary.models import *

hmap = {
    1: '\u00b9',
    2: '\u00b2',
    3: '\u00b3',
    4: '\u2074',
    None: '',
}

def e_template(entries):
    return ', '.join(
        '%s%s' % (i.civil_equivalent, hmap[i.homonym_order])
        for i in entries)

def cg_template(collogroups):
    return ', '.join(
        cg.collocations[0].civil_equivalent
        for cg in collogroups)

def m_template(mes):
    x, y = [], []
    for m in mes:
        if isinstance(m.host, Entry):
            x.append('%s%s знач. %s' % (
                m.host.civil_equivalent,
                hmap[i.homonym_order],
                m.parent_meaning.order if m.parent_meaning else m.order))
        else:
            y.append('%s знач. %s' % (
                m.host.collocations[0].civil_equivalent,
                m.parent_meaning.order if m.parent_meaning else m.order))
    return ', '.join(x), ', '.join(y)

e_all, cg_all, me_all, mcg_all = [], [], [], []
e_e, e_cg, e_me, e_mcg = [], [], [], []
cg_e, cg_cg, cg_me, cg_mcg = [], [], [], []
me_e, me_cg, me_me, me_mcg = [], [], [], []
mcg_e, mcg_cg, mcg_me, mcg_mcg = [], [], [], []

# Ссылки вида "ср." от слов
entries = []
for e in Entry.objects.order_by('civil_equivalent'):
    es, cgs, mes, mcgs = [''] * 4

    if e.cf_entries.exists():
        es = e_template(e.cf_entries.all())

    if e.cf_collogroups.exists():
        cgs = cg_template(e.cf_collogroups.all())

    if e.cf_meanings.exists():
        mes, mcgs = m_template(e.cf_meanings.all())

    if es or cgs or mes or mcgs:
        etxt =  '%s%s' % (e.civil_equivalent, hmap[e.homonym_order])
        item = (etxt, es, cgs, mes, mcgs)
        entries.append(item)

entries.sort()
e_all = ['%s ср. %s' % (i[0], '; '.join(j for j in i[1:] if j))
         for i in entries]
e_e = ['%s ср. %s' % i[:2] for i in entries if i[1]]
e_cg = ['%s ср. %s' % (i[0], i[2]) for i in entries if i[2]]
e_me = ['%s ср. %s' % (i[0], i[3]) for i in entries if i[3]]
e_mcg = ['%s ср. %s' % (i[0], i[4]) for i in entries if i[4]]

f = open('entries_cf.txt', 'w')
text = '\n'.join(e_all)
f.write(text + '\n')
f.close()

f = open('entries_cf_grouped.txt', 'w')
text = '''
Ссылки на слова
===============
'''
text += '\n'.join(e_e)
text += '''

Ссылки на словосочетания
========================
'''
text += '\n'.join(e_cg)
text += '''

Ссылки на значения слов
=======================
'''
text += '\n'.join(e_me)
text += '''

Ссылки на значения словосочетаний
=================================
'''
text += '\n'.join(e_mcg)
text += '\n'
f.write(text)
f.close()
