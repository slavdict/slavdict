# -*- coding: utf-8 -*-
from django.db import transaction

from slavdict.dictionary.models import *


def cf(civil_equivalents):
    u'''Расстановка взаимных ссылок вида "ср." между словарными статьями.'''
    entries = []
    civil_equivalents = [x.strip() for x in civil_equivalents.split() if x.strip()]
    for ce in civil_equivalents:
        _entries = Entry.objects.filter(civil_equivalent=ce).order_by('homonym_order')
        if _entries.count() > 1:
            for e in _entries:
                print '%s %s [%s] %s' % (
                        e.civil_equivalent, e.homonym_order, e.homonym_gloss,
                        e.get_part_of_speech_display())
            x = raw_input('\nIndicate homonym indices you want to use,'
                          'e.g. "1, 3": ').strip()
            if x:
                x = [int(i) for i in x.split(',')]
            else:
                x = [e.homonym_order for e in _entries]
            _entries = [e for e in _entries if e.homonym_order in x]
        entries.extend(_entries)
    print 'Entries:', [e.pk for e in entries]
    for entry in entries:
        print '%d %s --> %r\n    %s' % (
                entry.pk, entry.civil_equivalent,
                [e.pk for e in entry.cf_entries.all()],
                entry.additional_info)
    if len(entries) != len(civil_equivalents):
        print ('\033[0;31mFound %d entries '
               'for %d civil equivalents\033[0m' % (
                                    len(entries), len(civil_equivalents)))
    with transaction.atomic():
        for entry in entries:
            entry.cf_entries = set(entry.cf_entries.all()) | set(
                                        e for e in entries if e.pk != entry.pk)
            print '\n\n%d %s\n    %s' % (
                    entry.pk, entry.civil_equivalent, entry.additional_info)
            x = raw_input('\nDelete [d], change [c] or do nothing [N]\n'
                          'with ``additional_info``: ')
            x = x.decode('utf-8').lower() or u'n'
            if x in (u'd', u'в'):
                entry.additional_info = u''
                entry.save()
            elif x in (u'c', u'с'):
                x = raw_input('Input new ``additional_info``: ').decode('utf-8')
                entry.additional_info = x
                entry.save()
    return list(entries)

# vi: set ai et sw=4 ts=4 :
