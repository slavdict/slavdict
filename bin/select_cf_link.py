# coding: utf-8
from slavdict.dictionary.models import *

hmap = {
    1: u'\u00b9',
    2: u'\u00b2',
    3: u'\u00b3',
    4: u'\u2074',
    None: u'',
}

def e_template(entries):
    return u', '.join(
        u'%s%s' % (i.civil_equivalent, hmap[i.homonym_order])
        for i in entries)

def cg_template(collogroups):
    return u', '.join(
        cg.collocations[0].civil_equivalent
        for cg in collogroups)

def m_template(mes):
    x, y = [], []
    for m in mes:
        if isinstance(m.host, Entry):
            x.append(u'%s%s знач. %s' % (
                m.host.civil_equivalent,
                hmap[i.homonym_order],
                m.parent_meaning.order if m.parent_meaning else m.order))
        else:
            y.append(u'%s знач. %s' % (
                m.host.collocations[0].civil_equivalent,
                m.parent_meaning.order if m.parent_meaning else m.order))
    return u', '.join(x), u', '.join(y)

entries, collogroups, meaningse, meaningscg = [], [], [], []
e_all, cg_all, me_all, mcg_all = [], [], [], []
e_e, e_cg, e_me, e_mcg = [], [], [], []
cg_e, cg_cg, cg_me, cg_mcg = [], [], [], []
me_e, me_cg, me_me, me_mcg = [], [], [], []
mcg_e, mcg_cg, mcg_me, mcg_mcg = [], [], [], []

for e in Entry.objects.order_by('civil_equivalent'):
    cf_entries, cf_collogroups = [u''] * 2
    cf_meanings_e, cf_meanings_c = [u''] * 2

    if e.cf_entries.exists():
        cf_entries = e_template(e.cf_entries.all())

    if e.cf_collogroups.exists():
        cf_collogroups = cg_template(e.cf_collogroups.all())

    if e.cf_meanings.exists():
        cf_meanings_e, cf_meanings_c = m_template(e.cf_meanings.all())

    if cf_entries or cf_collogroups or cf_meanings_e or cf_meanings_c:
        etxt =  u'%s%s' % (e.civil_equivalent, hmap[e.homonym_order])
        item = (etxt, cf_entries, cf_collogroups,
                cf_meanings_e, cf_meanings_c)
        entries.append(item)

entries.sort()
e_all = [u'%s ср. %s' % (i[0], u'; '.join(j for j in i[1:] if j))
         for i in entries]
e_e = [u'%s ср. %s' % i[:2] for i in entries if i[1]]
e_cg = [u'%s ср. %s' % (i[0], i[2]) for i in entries if i[2]]
e_me = [u'%s ср. %s' % (i[0], i[3]) for i in entries if i[3]]
e_mcg = [u'%s ср. %s' % (i[0], i[4]) for i in entries if i[4]]

f = open('entries_cf.txt', 'w')
text = u'\n'.join(e_all)
f.write(text.encode('utf-8') + '\n')
f.close()

f = open('entries_cf_grouped.txt', 'w')
text = u'''
Ссылки на слова
===============
'''
text += u'\n'.join(e_e)
text += u'''

Ссылки на словосочетания
========================
'''
text += u'\n'.join(e_cg)
text += u'''

Ссылки на значения слов
=======================
'''
text += u'\n'.join(e_me)
text += u'''

Ссылки на значения словосочетаний
=================================
'''
text += u'\n'.join(e_mcg)
text += u'\n'
f.write(text.encode('utf-8'))
f.close()
        
