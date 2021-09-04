import os
import re

from django.db import transaction

from slavdict.dictionary.models import *

EDITOR = os.environ.get('EDITOR','vi')

def edit(ge):
    print('Редактирование не реализовано')
    input()

for ge in GreekEquivalentForExample.objects.all():
    if ('...' in ge.unitext or '…' in ge.unitext) and ge.host_entry.is_in_volume(1):
        host_entry = ge.host_entry.civil_equivalent
        host = ge.host.civil_equivalent
        print(host_entry, ':', host if host != host_entry else '')
        print(ge.for_example.example)
        example = ge.for_example
        greek_equivs = list(example.greek_equivs)
        position = greek_equivs.index(ge)
        if len(greek_equivs) > 1:
            print('%s [%s]' %  (ge.unitext, '; '.join(x for x in greek_equivs)))
        else:
            print(ge.unitext)

        x = input('\nРазбить по многоточию? (yes/NO/edit/quit): ')
        x = x.strip().lower()
        if not x or 'no'.startswith(x) or 'нет'.startswith(x):
            continue
        elif 'edit'.startswith(x):
            edit(ge)
        elif 'quit'.startswith(x):
            break
        else:
            with transaction.atomic():
                for i, part in enumerate(re.split('\.\.\.|…', ge.unitext)):
                    part = part.strip()
                    if i == 0:
                        ge.unitext = part
                        ge.order = i + position
                        ge.save(without_mtime=True)
                    else:
                        ge = GreekEquivalentForExample(for_example=example,
                                unitext=part, initial_form='',
                                initial_form_phraseology='',
                                mark='', source='', note='',
                                additional_info='', order=i+position)
                        ge.save(without_mtime=True)
                if len(greek_equivs) > 1:
                    for j, ge in enumerate(greek_equivs):
                        if j != position:
                            ge.order = j if j < position else j + i
                            ge.save(without_mtime=True)

# vi: set ai et sw=4 ts=4 :
