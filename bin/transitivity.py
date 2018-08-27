# -*- coding: utf-8 -*-
from itertools import chain

from slavdict.dictionary.models import *

def transitivity(arg):
    if isinstance(arg, int):
        e = Entry.objects.get(pk=arg)
    elif isinstance(arg, Entry):
        e = arg
    else:
        print 'wrong argument:', arg
        return

    if not e.is_part_of_speech('verb'):
        print u'Лексема не является глаголом.'
        return

    for meaning in e.meanings:
        print
        print e.civil_equivalent
        if meaning.transitivity:
            print u'\t' + meaning.get_transitivity_display()
        else:
            print u'\t[переходность не задана]'
        print u'\t%s' % meaning.meaning, u'|', meaning.gloss

        for ex in chain(meaning.examples,
                *(m.examples for m in meaning.child_meanings)):
            print u'\t\t* %s' % ex.example

        while True:
            x = raw_input((u'''
    Что с переходностью? Перех./неперех./смешанный [%s/%s/%s]
    (Enter = ничего не менять): ''' % (
            TRANSITIVITY_MAP['transitive'],
            TRANSITIVITY_MAP['intransitive'],
            TRANSITIVITY_MAP['labile'],
            )).encode('utf-8'))
            x = x.lower().strip()
            if x == TRANSITIVITY_MAP['transitive']:
                meaning.transitivity = TRANSITIVITY_MAP['transitive']
                meaning.save(without_mtime=True)
                break
            elif x == TRANSITIVITY_MAP['intransitive']:
                meaning.transitivity = TRANSITIVITY_MAP['intransitive']
                meaning.save(without_mtime=True)
                break
            elif x == TRANSITIVITY_MAP['labile']:
                meaning.transitivity = TRANSITIVITY_MAP['labile']
                meaning.save(without_mtime=True)
                break
            elif not x:
                break
            else:
                print u'''
    Символ %r недопустим для выбора. Введите заново.''' % x


# vi: set ai et sw=4 ts=4 :
