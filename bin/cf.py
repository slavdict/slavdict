# -*- coding: utf-8 -*-
from django.db import transaction

from slavdict.dictionary.models import *


def cf(civil_equivalents):
    entries = Entry.objects.filter(civil_equivalent__in=civil_equivalents)
    print 'Found %d entries for %d civil equivalents' % (
           len(entries), len(civil_equivalents))
    print 'Entries:', [e.pk for e in entries]
    for e in entries:
        print '%d --> %r' % (e.pk, [e.pk for e in e.cf_entries.all()])
        print '    %s' % e.additional_info
    with transaction.atomic():
        for entry in entries:
            entry.cf_entries = [e for e in entries if e.pk != entry.pk]
    return list(entries)

# vi: set ai et sw=4 ts=4 :
