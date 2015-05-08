# -*- coding: utf-8 -*-
from django.db import transaction

from slavdict.dictionary.models import *


def cf(civil_equivalents):
    entries = Entry.objects.filter(civil_equivalent__in=civil_equivalents)
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
            print '%d %s\n    %s' % (
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
