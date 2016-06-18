# -*- coding: utf-8 -*-
import os
import subprocess
import tempfile

from django.db import transaction

from slavdict.dictionary.models import *

EDITOR = os.environ.get('EDITOR','vi')

def subvariants(x):
    if isinstance(x, int):
        e = Entry.objects.get(pk=x)
    elif isinstance(x, Entry):
        e = x
    else:
        print 'wrong argument:', x
    ids = [o.id for o in e.orth_vars]

    with transaction.atomic():
        text = u''
        for basevar in e.base_vars:
            text += u'%s\t%s\n' % (basevar.pk, basevar.idem)
            for subvar in basevar.children.all():
                text += u'\t%s\t%s\n' % (subvar.pk, subvar.idem)

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(text.encode('utf-8'))
            tf.flush()
            subprocess.call([EDITOR, tf.name])
            tf.seek(0)
            edited_text = tf.readlines()

        n = 0
        parent = None
        for line in edited_text:
            n += 1
            oid = int(line.lstrip().split('\t', 1)[0])
            assert oid in ids
            o = OrthographicVariant.objects.get(pk=oid)
            o.order = n
            if line.lstrip() == line:
                o.parent = None
                parent = o
            else:
                o.parent = parent
            o.save()

        text = u''
        for basevar in e.base_vars:
            text += u'%s\t%s\n' % (basevar.pk, basevar.idem)
            for subvar in basevar.children.all():
                text += u'\t%s\t%s\n' % (subvar.pk, subvar.idem)
        print text

# vi: set ai et sw=4 ts=4 :
