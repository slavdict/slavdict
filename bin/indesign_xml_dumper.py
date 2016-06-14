#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import os
import re
import sys

import django
from coffin.shortcuts import render_to_string

sys.path.append(os.path.abspath('../slavdict'))
from slavdict import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

def sort_key(word):
    w1 = w2 = word
    level1 = (
        (ur"['`\^\~А-ЯЄЅІЇѠѢѤѦѨѪѬѮѰѲѴѶѸѺѼѾ]", u''),
        (u'ъ',      u''),
        (u'аѵ',     u'ав'),
        (u'[еє]ѵ',  u'ев'),
        (u'ѯ',      u'кс'),
        (u'ѿ',      u'от'),
        (u'ѱ',      u'пс'),

        (u'а',      u'00'),
        (u'б',      u'01'),
        (u'в',      u'02'),
        (u'г',      u'03'),
        (u'д',      u'04'),
        (u'[еєѣ]',  u'05'),
        (u'ж',      u'06'),
        (u'[зѕ]',   u'07'),
        (u'[иіїѵ]', u'08'),
        (u'й',      u'09'),
        (u'к',      u'10'),
        (u'л',      u'11'),
        (u'м',      u'12'),
        (u'н',      u'13'),
        (u'[оѻѡѽ]', u'14'),
        (u'п',      u'15'),
        (u'р',      u'16'),
        (u'с',      u'17'),
        (u'т',      u'18'),
        (u'[уѹꙋ]',  u'19'),
        (u'[фѳ]',   u'20'),
        (u'х',      u'21'),
        (u'ц',      u'22'),
        (u'ч',      u'23'),
        (u'ш',      u'24'),
        (u'щ',      u'25'),
        (u'ы',      u'26'),
        (u'ь',      u'27'),
        (u'ю',      u'28'),
        (u'[ѧꙗ]',   u'29'),
    )
    level2 = (
        (ur"([аеє])(['`\^]?)ѵ", ur'\g<1>\g<2>01'),

        (ur"'",     u'31'),
        (ur"`",     u'32'),
        (ur"\^",    u'33'),
        (ur"\~",    u'40'),
        (ur"[А-ЩЫ-ЯЄЅІЇѠѢѤѦѨѪѬѮѰѲѴѶѸѺѼѾ]", u'50'),

        (u'Ъ',      u'01'),
        (u'ъ',      u'02'),

        (u'ѯ',      u'0100'),
        (u'ѱ',      u'0100'),

        (u'е',  u'00'),
        (u'є',  u'01'),
        (u'ѣ',  u'02'),

        (u'ѕ',  u'01'),
        (u'з',  u'02'),

        (u'и',    u'00'),
        (u'[ії]', u'01'),
        (u'ѵ',    u'02'),

        (u'о', u'00'),
        (u'ѻ', u'01'),
        (u'ѡ', u'02'),
        (u'ѿ', u'0200'),
        (u'ѽ', u'03'),

        (u'ѹ', u'00'),
        (u'ꙋ', u'01'),
        (u'у', u'02'),

        (u'ф', u'00'),
        (u'ѳ', u'01'),

        (u'ѧ', u'00'),
        (u'ꙗ', u'01'),

        (u'[а-я]', u'00'),
    )

    for pattern, substitution in level1:
        w1 = re.sub(pattern, substitution, w1)

    for pattern, substitution in level2:
        w2 = re.sub(pattern, substitution, w2)

    return (w1, w2)




from slavdict.dictionary.models import Entry, OrthographicVariant

#entries = [e for e in Entry.objects.all()
#             if e.orth_vars[0].idem.startswith((u'а', u'А', u'б', u'Б'))]
#entries = [(e, render_to_string('indesign/e.xml', {'entry': e}).strip())
#           for e in entries]
#entries.sort(key=lambda x: x[0].orth_vars[0].idem)
#
#for e, _ in entries:
#    if e.orth_vars_refs[1:] or e.nom_sg or e.participles:
#
#        text = e.orth_vars_refs[0].idem
#        print text.encode('utf-8')
#
#        orthvars = [o.idem for o in e.orth_vars_refs[1:]]
#        participles = [p.idem for p in e.participles]
#        nom_sg = [e.nom_sg] if e.nom_sg else []
#        text = u'    %s\n' % u' '.join(orthvars + nom_sg + participles)
#        print text.encode('utf-8')

entries = [ov.idem for ov in OrthographicVariant.objects.all()] + \
          [e.nom_sg for e in Entry.objects.all() if e.nom_sg] + \
          [p.idem for e in Entry.objects.all() for p in e.participles] + \
          [e.short_form for e in Entry.objects.all() if e.short_form]
entries.sort(key=sort_key)
for e in entries:
    print e.encode('utf-8')

sys.exit(0)
