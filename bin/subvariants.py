# -*- coding: utf-8 -*-
import os
import re
import subprocess
import tempfile

from django.db import transaction

from slavdict.dictionary.models import *

EDITOR = os.environ.get('EDITOR','vi')

def subvariants(arg):
    if isinstance(arg, int):
        e = Entry.objects.get(pk=arg)
    elif isinstance(arg, Entry):
        e = arg
    else:
        print 'wrong argument:', arg
    ids = [o.id for o in e.orth_vars]

    with transaction.atomic():
        text = u''
        for basevar in e.base_vars:
            text += u'%s\t%s\n' % (basevar.pk, basevar.idem)
            for subvar in basevar.children.all():
                text += u'\t%s\t%s\n' % (subvar.pk, subvar.idem)
        print
        print text

        text += u'''
# Для изменения порядка следования вариантов расположите строки в нужном
# порядке. Иерархические отношения задавайте отступами в начале строки. Если
# отступ в начале строки есть, значит данный вариант является подвариантом
# предшествующего варианта без отступа.
#
# Для добавления нового варианта вместо числового идентификатора поставьте
# знак плюса. Для удаления варианта добавьте впритык к идентификатору минус
# слева или справа.'''

        with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
            tf.write(text.encode('utf-8'))
            tf.flush()
            subprocess.call([EDITOR, tf.name])
            tf.seek(0)
            edited_text = tf.readlines()

        n = 0
        parent = None
        r = re.compile(u'\s+')
        for line in filter(lambda x:x.strip() and x[:1] != u'#', edited_text):
            n += 1
            oid, wordform = r.split(line.strip())
            if oid == '+':
                o = OrthographicVariant(idem=wordform, entry=e)
            elif oid.strip('-').isdigit():
                if u'-' in oid:
                    do_delete = True
                else:
                    do_delete = False
                if do_delete:
                    oid = int(oid.strip('-'))
                    for oo in e.orth_vars:
                        if oo.parent and oo.parent.id == oid:
                            oo.parent = None
                            oo.save()
                else:
                    oid = int(oid)
                assert oid in ids
                o = OrthographicVariant.objects.get(pk=oid)
                if do_delete:
                    o.delete()
                    continue
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
        print '-' * 10
        print text

    x = raw_input(u'\nЗакончить редактирование? (Y/n): '.encode('utf-8'))
    x = x.strip()
    if not x or x.lower() in ('y', 'ye', 'yes', u'да', u'д'):
        pass
    else:
        subvariants(arg)

# vi: set ai et sw=4 ts=4 :
