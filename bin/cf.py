# -*- coding: utf-8 -*-
from django.db import transaction

from slavdict.dictionary.models import *


def cf(civil_equivalents):
    ''' Расстановка взаимных ссылок вида "ср." между словарными статьями.'''
    entries = []
    for ce in civil_equivalents:
        _entries = Entry.objects.filter(civil_equivalents=ce).order_by('homonym_number')
        if _entries.count() > 1:
            for e in _entries:
                print '%s %s [%s] %s' % (
                        e.civil_equivalent, e.homonym_number, e.homonym_gloss,
                        e.get_part_of_speech_display())
            x = raw_input('\nIndicate homonym indices you want to use,'
                          'e.g. "1, 3": ').split(',')
            x = [int(i) for i in x] or [e.homonym_number for e in _entries]
            _entries = [e for e in _entries if e.homonym_number in x]
        entries.extend(_entries)
    print 'Found %d entries for %d civil equivalents' % (
           len(entries), len(civil_equivalents))
    print 'Entries:', [e.pk for e in entries]
    for entry in entries:
        print '%d %s --> %r\n    %s' % (
                entry.pk, entry.civil_equivalent,
                [e.pk for e in entry.cf_entries.all()],
                entry.additional_info)
    with transaction.atomic():
        for entry in entries:
            entry.cf_entries = [e for e in entries if e.pk != entry.pk]
            print '\n\n%d %s\n    %s' % (
                    entry.pk, entry.civil_equivalent, entry.additional_info)
            x = raw_input('\nDelete [d], change [c] or do nothing [N]\n'
                          'with ``additional_info``: ').lower() or 'n'
            if x == 'd':
                entry.additional_info = u''
                entry.save()
            elif x == 'c':
                x = raw_input('Input new ``additional_info``: ').decode('utf-8')
                entry.additional_info = x
                entry.save()
    return list(entries)

# vi: set ai et sw=4 ts=4 :
