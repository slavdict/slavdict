from django.db import transaction

from slavdict.dictionary.models import *


def merge_entries(dst_id, src_id):
    e1 = Entry.objects.get(pk=dst_id)
    e2 = Entry.objects.get(pk=src_id)
    with transaction.atomic():
        for ex in e2.example_set.all():
            ex.entry = e1
            ex.save()
        for m in e2.meaning_set.all():
            if m.entry_container is not None and m.entry_container == e2:
                m.entry_container = e1
                m.order = m.order + 1000
                m.save()
        e1.duplicate = False
        e1.save()
        e2.duplicate = False
        e2.save()
        for a in e2.authors.all():
            e1.authors.add(a)
        print(dst_id)
        print('"cf." references: <-- %r, --> %r' % (
                [e.pk for e in e1.cf_entry_set.all()],
                [e.pk for e in e1.cf_entries.all()]))
        print('"see" references: <-- %r, --> %r' % (
                [e.pk for e in e1.ref_entry_set.all()],
                e1.link_to_entry.pk if e1.link_to_entry else None))
        print(src_id)
        print('"cf." references: <-- %r, --> %r' % (
                [e.pk for e in e2.cf_entry_set.all()],
                [e.pk for e in e2.cf_entries.all()]))
        print('"see" references: <-- %r, --> %r' % (
                [e.pk for e in e2.ref_entry_set.all()],
                e2.link_to_entry.pk if e2.link_to_entry else None))
    return e1, e2

# vi: set ai et sw=4 ts=4 :
