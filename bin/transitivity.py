# -*- coding: utf-8 -*-
from itertools import chain

from slavdict.dictionary.models import *

def distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n
    cur_row = range(n+1)  # Keep current and previous row, not entire matrix
    for i in range(1, m+1):
        pre_row, cur_row = cur_row, [i]+[0]*n
        for j in range(1,n+1):
            add, delete, change = pre_row[j]+1, cur_row[j-1]+1, pre_row[j-1]
            if a[j-1] != b[i-1]:
                change += 1
            cur_row[j] = min(add, delete, change)
    return cur_row[n]

def leading_similariry(a, b):
    "Определяет сколько символов в начале слов совпадает"
    i = 0
    a = a.lower()
    b = b.lower()
    for c1, c2 in zip(a, b):
        if c1 == c2:
            i += 1
        else:
            break
    return i

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
        print u'\033[1;36m%s\033[0m' % e.civil_equivalent
        if meaning.transitivity:
            print u'\t' + meaning.get_transitivity_display()
        else:
            print u'\t[переходность не задана]'
        print u'\t%s' % meaning.meaning, u'|', meaning.gloss

        for ex in chain(meaning.examples,
                *(m.examples for m in meaning.child_meanings)):
            example = civilrus_convert(ex.example)
            words_lds = [(w, distance(e.civil_equivalent, w.lower()) -
                             leading_similariry(e.civil_equivalent, w.lower()))
                         for w in example.split()]
            ld_min = min(ld for w, ld in words_lds)
            words = [u'\033[1;33m%s\033[0m' % w if ld == ld_min else w
                     for w, ld in words_lds]
            print u'\t\t*  %s' % u' '.join(words)

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
