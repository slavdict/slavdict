#!/usr/bin/env python
"""
Скрипт делает XML-выгрузку словарной базы для InDesign.

При необходимости сделать выборочную выгрузку скрипту допустимо передавать
номера статей в качестве аргументов. Каждый номер можно отделять от другого
пробелами, запятыми или запятыми с пробелами, например:

    SCRIPT 1177,123 89 945, 234
"""
import datetime
import itertools
import os
import re
import signal
import sys

import django
from django.db.models import Q
from django.template.loader import render_to_string
from functools import reduce

sys.path.append(os.path.abspath('/var/www/slavdict'))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.constants import CURRENT_VOLUME
from slavdict.dictionary.constants import VOLUME_LETTERS
from slavdict.dictionary.models import Entry
from slavdict.dictionary.utils import civilrus_convert
from slavdict.dictionary.utils import resolve_titles
from slavdict.dictionary.utils import sort_key1
from slavdict.dictionary.utils import sort_key2
from slavdict.dictionary.utils import ucs_convert

OUTPUT_VOLUMES = (CURRENT_VOLUME,)
OUTPUT_VOLUMES_LETTERS = reduce(lambda x, y: x + y, (VOLUME_LETTERS[volume]
    for volume in OUTPUT_VOLUMES if volume in VOLUME_LETTERS), ())

sbl_arg = '--split-by-letters'
snc_arg = '--split-nchars='
opp_arg = '--output-pattern='
opv_arg = '--output-volumes='
SPLIT_BY_LETTERS = False
SPLIT_NCHARS = 0
OUTPUT_PATTERN = '/root/slavdict-indesign-#.xml'

CSI = '\033['
HIDE_CURSOR = CSI + '?25l'
SHOW_CURSOR = CSI + '?25h'
ERASE_LINE = CSI + '2K'
ERASE_LINEEND = CSI + '0K'

DATETIME = datetime.datetime.now()

def interrupt_handler(signum, frame):
    print(SHOW_CURSOR, file=sys.stderr)
    sys.exit(1)

for sig in (signal.SIGINT, signal.SIGTERM, signal.SIGILL, signal.SIGHUP):
    signal.signal(sig, interrupt_handler)

print(HIDE_CURSOR, file=sys.stderr)
note =  'Volumes: ' + ', '.join(str(volume) for volume in OUTPUT_VOLUMES) + '\n'
note += 'Letters: ' + ', '.join(letter for letter in OUTPUT_VOLUMES_LETTERS)
print(note + '\n', file=sys.stderr)

def in_output_volumes(wordform):
    civil = civilrus_convert(resolve_titles(wordform.strip(' *')))
    return civil[:1].lower() in OUTPUT_VOLUMES_LETTERS

entries1 = []
# Это список всех потенциально возможных статей для выбранных томов,
# ограниченных списками test_entry_ids и test_entry_cequivs, если они заданы.

lexemes = Entry.objects.all()
test_entry_ids = []
test_entry_cequivs = []
if len(sys.argv) > 1:
    args = []
    for i, arg in enumerate(sys.argv[1:]):
        if arg.startswith(sbl_arg):
            SPLIT_BY_LETTERS = True
        elif arg.startswith(snc_arg):
            SPLIT_NCHARS = int(re.sub(r'[^\d]', '', arg) or 0)
        elif arg.startswith(opp_arg):
            OUTPUT_PATTERN = arg[len(opp_arg):]
        elif arg.startswith(opv_arg):
            try:
                OUTPUT_VOLUMES = arg[len(opv_arg):]
            except:
                sys.exit(1)
        else:
            args.append(arg)
    r = re.compile(r'\s*,\s*|\s+')
    s = ' '.join(args).strip(' ,')
    for x in r.split(s):
        if x.isnumeric():
            test_entry_ids.append(int(x))
        else:
            test_entry_cequivs.append(x)

print('Make multiple files according '
      'to the first letter:', SPLIT_BY_LETTERS, file=sys.stderr)
print('Make multiple files when number of non tag '
      'characters is greater than:', SPLIT_NCHARS, file=sys.stderr)
print('Output pattern:', OUTPUT_PATTERN, file=sys.stderr)
if test_entry_ids or test_entry_cequivs:
    q = Q()
    if test_entry_ids:
        print('Entry ids to dump:',
              ', '.join(str(i) for i in test_entry_ids), file=sys.stderr)
        q |= Q(pk__in=test_entry_ids)
    if test_entry_cequivs:
        print('Entries to dump:',
              ', '.join(str(i) for i in test_entry_ids), file=sys.stderr)
        q |= Q(civil_equivalent__in=test_entry_cequivs)
    lexemes = lexemes.filter(q)
else:
    print('Entries to dump: ALL for the selected volumes', file=sys.stderr)
lexemes = [e for e in lexemes if e.is_in_volume(OUTPUT_VOLUMES)]
lexemes_n = len(lexemes)
print('Number of selected lexemes:', lexemes_n, file=sys.stderr)
print(file=sys.stderr)

for i, lexeme in enumerate(lexemes):

    wordform = lexeme.base_vars[0].idem
    reference = None
    entries1.append((wordform, reference, lexeme))
    key = sort_key1(wordform)

    # Разные ссылочные статьи в пределах выбранных томов

    # 1) Варианты заглавного слова
    for var in lexeme.orth_vars_refs[1:]:
        wordform2 = resolve_titles(var.idem)
        if wordform2 != var.idem:
            continue
        key2 = sort_key1(wordform2)
        if key2 != key:
            reference = ucs_convert(wordform2)
            entries1.append((wordform2, reference, lexeme))

    # 2) Названия народов
    COMMA = r',\s+'
    if lexeme.nom_pl:
        wordform = lexeme.nom_pl
        reference = lexeme.nom_pl_ucs_wax[1]
        for wordform, reference in zip(
                re.split(COMMA, wordform), re.split(COMMA, reference)):
            entries1.append((wordform, reference, lexeme))

    # 3) Краткие формы
    #if lexeme.short_form:
    #    wordform = lexeme.short_form
    #    reference = lexeme.short_form_ucs
    #    entries1.append((wordform, reference, lexeme))

    # 4) Причастия
    #for participle in lexeme.participles:
    #    wordform = participle.idem
    #    reference = participle.idem_ucs
    #    entries1.append((wordform, reference, lexeme))

    # 5) Особые случаи
    if lexeme.civil_equivalent == 'быти':
        for wordform in ("бꙋ'дꙋчи", "сы'й", "сꙋ'щiй"):
            reference = ucs_convert(wordform)
            entries1.append((wordform, reference, lexeme))
    elif lexeme.civil_equivalent == 'утрие':
        for wordform in ("воꙋ'тріе", "воꙋ'тріи", "воꙋ'тріѧ"):
            reference = ucs_convert(wordform)
            entries1.append((wordform, reference, lexeme))

    note = 'Отбор претендентов на вокабулы [ %s%% ] %s\r' % (
        int(round(i / lexemes_n * 100)),
        lexeme.civil_equivalent + ERASE_LINEEND)
    sys.stderr.write(note)

if not test_entry_ids and not test_entry_cequivs:
    #     6) Добавляем ссылочные статьи, которые будут присутствовать в выводимых
    #        томах и ссылаться на какие-то статьи из других томов.
    other_volumes = [e for e in Entry.objects.all()
                       if not e.is_in_volume(OUTPUT_VOLUMES)]
    other_volumes_n = len(other_volumes)
    for i, lexeme in enumerate(other_volumes):
        for participle in lexeme.participles:
            if participle.tp not in ('1', '2', '3', '4'):
                wordform = participle.idem
                if in_output_volumes(wordform):
                    reference = participle.idem_ucs
                    entries1.append((wordform, reference, lexeme))

        note = 'Поиск ссылок на другие тома [ %s%% ] %s\r' % (
            int(round(i / other_volumes_n * 100)),
            lexeme.civil_equivalent + ERASE_LINEEND)
        sys.stderr.write(note)

def sort_key(x):
    wordform, reference, lexeme = x
    if reference:
        ref_wordform = lexeme.base_vars[0].idem
        key = (sort_key1(wordform), -1, sort_key2(wordform),
               sort_key1(ref_wordform), lexeme.homonym_order or 0, sort_key2(ref_wordform))
    else:
        key = sort_key1(wordform), lexeme.homonym_order or 0, sort_key2(wordform)
    return key

note = 'Сортировка результатов...' + ERASE_LINEEND + '\r'
sys.stderr.write(note)
entries1 = sorted(set(entries1), key=sort_key)
entries1_n = len(entries1)

entries2 = []
# Список статей, где ссылочные статьи сгруппированы по номеру омонима

for i, (key, group) in enumerate(itertools.groupby(entries1, lambda x: x[:2])):
    wordform, reference = key
    note = 'Группировка ссылочных статей [ %s%% ] %s\r' % (
        int(round(i / entries1_n * 100)),
        wordform + ERASE_LINEEND)
    sys.stderr.write(note)
    if not in_output_volumes(wordform):
        continue
    # FIXME: Удаляем из выгрузки отсылочную статью Ассирии,
    # т.к. она неправильно выгружается
    if wordform == "ассѵрі'и":
        continue
    lst = list(group)
    if len(lst) < 2:
        wordform, reference, lexeme = lst[0]
        entries2.append((wordform, reference, lexeme))
    else:
        if reference is None:  # Статьи не ссылочные
            for wordform, reference, lexeme in lst:
                entries2.append((wordform, reference, lexeme))
        else:  # Статьи ссылочные
            lst = [x[2] for x in sorted(lst, key=sort_key)]
            lexeme = {
                'is_reference': True,
                'referenced_lexemes': lst,
            }
            if all(x.homonym_order for x in lst):
                lexeme['references'] = [
                    { 'reference_ucs': lst[0].base_vars[0].idem_ucs,
                      'homonym_order': ',\u00a0'.join(
                         str(i.homonym_order)
                         for i in lst if i
                      )
                    }
                ]
            else:
                lexeme['references'] = [
                    { 'reference_ucs': x.base_vars[0].idem_ucs,
                      'homonym_order': x.homonym_order or None }
                    for x in lst
                ]
            entries2.append((wordform, reference, lexeme))
entries2_n = len(entries2)


def upper_cond(i, entry_list):
    _, _, lexeme1 = entry_list[i]
    if isinstance(lexeme1, dict) and len(lexeme1['referenced_lexemes']) > 1:
        return True
    n_entry_list = len(entry_list)
    j = i + 1
    while (j < n_entry_list):
        _, reference2, lexeme2 = entry_list[j]
        if not reference2:
            return lexeme2.id != lexeme1.id
        else:
            if isinstance(lexeme2, Entry) and lexeme1.id != lexeme2.id:
                return True
            elif isinstance(lexeme2, dict):
                lxs = lexeme2['referenced_lexemes']
                if len(lxs) > 1 or lexeme1.id != lxs[0].id:
                    return True
        j += 1
    return True

def lower_cond(i, entry_list):
    _, _, lexeme1 = entry_list[i]
    if isinstance(lexeme1, dict) and len(lexeme1['referenced_lexemes']) > 1:
        return True
    j = i - 1
    while (j > 0):
        _, reference2, lexeme2 = entry_list[j]
        if not reference2:
            return lexeme2.id != lexeme1.id
        else:
            if isinstance(lexeme2, Entry) and lexeme1.id != lexeme2.id:
                return True
            elif isinstance(lexeme2, dict):
                lxs = lexeme2['referenced_lexemes']
                if len(lxs) > 1 or lexeme1.id != lxs[0].id:
                    return True
        j -= 1
    return True

entries3 = []
# Список статей, в том числе ссылочных, но с устранением ссылок,
# расположенных вплотную к целевым статьям

for i, (wordform, reference, lexeme) in enumerate(entries2):
    note = 'Устранение ссылок, примыкающих к целевым статьям [ %s%% ]%s\r' % (
            int(round(i / entries2_n * 100)), ERASE_LINEEND)
    sys.stderr.write(note)
    if not reference or upper_cond(i, entries2) and lower_cond(i, entries2):
        entries3.append((wordform, reference, lexeme))

class Reference(str):
    def __new__(cls, string, homonym_order=None):
        instance = str.__new__(cls, string)
        instance.homonym_order = homonym_order
        return instance


# Объединение статей по начальным буквам
letter_parts = []
part_entries = []
first_letter = entries3[0][0].lstrip(' =*')[0]
civil_letter = civilrus_convert(first_letter.lower())
csl_letter = first_letter.upper()
syn_letters = [csl_letter]
entries3_n = len(entries3)
for j, (wordform, group) in enumerate(itertools.groupby(entries3, lambda x: x[0])):
    note = 'Группировка статей по начальным буквам [ %s%% ]%s\r' % (
            int(round(j / entries3_n * 100)), ERASE_LINEEND)
    sys.stderr.write(note)
    lst = list(group)
    first_letter = wordform.lstrip(' =*')[0].lower()
    csl_letter = first_letter.upper()
    if civilrus_convert(first_letter) != civil_letter:
        syn_letters.sort(key=sort_key2)
        letter_parts.append((civil_letter, syn_letters, part_entries))
        part_entries = []
        civil_letter = civilrus_convert(first_letter)
        syn_letters = [csl_letter]
    elif csl_letter not in syn_letters:
        syn_letters.append(csl_letter)
    if len(lst) < 2:
        wordform, reference, lexeme = lst[0]
        part_entries.append((reference, lexeme))
    else:
        for i, (wordform, reference, lexeme) in enumerate(lst):
            if reference:
                reference = Reference(reference, homonym_order=i+1)
            else:
                lexeme.homonym_order = i + 1
            part_entries.append((reference, lexeme))
syn_letters.sort(key=sort_key2)
letter_parts.append((civil_letter, syn_letters, part_entries))

note = 'Вывод статей для InDesign...'
sys.stderr.write(note)

def render_chunks(c):
    return render_to_string('indesign/slavdict.xml', c)

def write_file(i, xml):
    subst = '{:%Y%m%d-%H%M%S}-{:03d}'.format(DATETIME, i)
    filepath = OUTPUT_PATTERN.replace('#', subst)
    open(filepath, 'w').write(xml)

C = ucs_convert
special_cases = [
    # агкир... см. анкир...  [анкира, анкирский]
    { 'startswith': [C("агкѵ'р")],
      'src': [{ 'ref': C("агкѵ'р"), 'dots': True }],
      'dst': [{ 'qv': C("анкѵ'р"), 'dots': True }] },

    # воутр... см. утрие.  [воутрие, воутрии, воутрия]
    { 'startswith': [C("воꙋ'тр")],
      'src': [{ 'ref': C("воꙋ'тр"), 'dots': True }],
      'dst': [{ 'qv': C("ѹ'тріе"), 'dots': False }] },

    # га'ггр... см. га'нгр...  [га'ггрена, гаггрский, гаггры, га'ггрянин]
    { 'startswith': [C("га'ггр")],
      'src': [{ 'ref': C("га'ггр"), 'dots': True }],
      'dst': [{ 'qv': C("га'нгр"), 'dots': True }] },

    # господьс... см. господс...  [господьский, господьственне, господьственно,
    #                              господьственный, господьствие, господьство,
    #                              господьствовати]
    { 'startswith': [C("госпо'дьс")],
      'src': [{ 'ref': C("госпо'дьс"), 'dots': True }],
      'dst': [{ 'qv': C("госпо'дс"), 'dots': True }] },

    # губител... см. губитель...  [губителный, губителство]
    { 'startswith': [C("гꙋби'тел")],
      'src': [{ 'ref': C("гꙋби'тел"), 'dots': True }],
      'dst': [{ 'qv': C("гꙋби'тель"), 'dots': True }] },

    # девор... и девwра см. деввwра.  [девора, деворра, девwра]
    { 'startswith': [C("дево'р"), C("девѡ'р")],
      'src': [
          { 'ref': C("дево'р"), 'dots': True },
          { 'ref': C("девѡ'ра"), 'dots': False },
      ],
      'dst': [{ 'qv': C("деввѡ'ра"), 'dots': False }] },

    # детищъ и детище см. детищь.  [детищъ, детище]
    { 'startswith': [C("дѣ'тищ")],
      'src': [
          { 'ref': C("дѣ'тищъ"), 'dots': False },
          { 'ref': C("дѣ'тище"), 'dots': False },
      ],
      'dst': [{ 'qv': C("дѣ'тищь"), 'dots': False }] },

    # доволн... см. довольн...  [доволне, доволно, доволнw, доволный]
    { 'startswith': [C("дово'лн")],
      'src': [{ 'ref': C("дово'лн"), 'dots': True }],
      'dst': [{ 'qv': C("дово'льн"), 'dots': True }] },

    # долн... см. дольний.  [долный, долний]
    { 'startswith': [C("до'лн")],
      'src': [{ 'ref': C("до'лн"), 'dots': True }],
      'dst': [{ 'qv': C("до'льній"), 'dots': False }] },

    # еврее и евреи см. евреанин, евреин.  [еврее, евреи]
    { 'startswith': [C("євре'є"), C("євре'и")],
      'src': [
          { 'ref': C("євре'є"), 'dots': False },
          { 'ref': C("євре'и"), 'dots': False },
      ],
      'dst': [
          { 'qv': C("євре'анинъ"), 'dots': False },
          { 'qv': C("євре'инъ"), 'dots': False }
      ] },

    # ермъ и ерма и ермей и ермий см. ермин.  [ермъ, ерма, ермей, ермий]
    { 'startswith': [C("є'рм"), C("єрм")],
      'src': [
          { 'ref': C("є'рмъ"), 'dots': False },
          { 'ref': C("є'рма"), 'dots': False },
          { 'ref': C("єрме'й"), 'dots': False },
          { 'ref': C("єрмі'й"), 'dots': False },
      ],
      'dst': [{ 'qv': C("єрмі'нъ"), 'dots': False }] },
]

SC_DICT_ERROR = 'Неправильные ключи в словаре `special_case`'
for sc in special_cases:
    if ('startswith' not in sc
            or 'src' not in sc
            or 'dst' not in sc):
        raise RuntimeError(SC_DICT_ERROR)
    for s in sc['src']:
        if 'ref' not in s or 'dots' not in s:
            raise RuntimeError(SC_DICT_ERROR)
    for s in sc['dst']:
        if 'qv' not in s or 'dots' not in s:
            raise RuntimeError(SC_DICT_ERROR)

chunks = []
n_chars = 0
file_count = 1
letters_and_chunks = []
for civil_letter, syn_letters, entries in letter_parts:
    letter = _letter = ', '.join(syn_letters)
    n_entries = len(entries)
    for i, (reference, entry) in enumerate(entries):
        if reference:
            special_case = None
            for sc in special_cases:
                if reference.startswith(tuple(sc['startswith'])):
                    special_case = sc
            if not special_case or 'used' not in special_case:
                try:
                    xml = render_to_string('indesign/slavdict_reference.xml', {
                        'reference': reference, 'entry': entry,
                        'special_case': special_case })
                except:
                    sys.stderr.write('    reference: %s\n' % reference)
                    sys.stderr.write('        entry: %s\n' % entry)
                    sys.stderr.write('special cases: %s\n' % special_cases)
                    raise
                if special_case:
                    special_case['used'] = True
            else:
                xml = ''
        else:
            xml = render_to_string('indesign/entry.xml', { 'entry': entry })

        xml = xml.strip()
        if xml:
            m = len(re.sub(r'<[^>]+>|\s', '', xml))
            if 0 < SPLIT_NCHARS < n_chars + m and 0 < n_chars:
                letters_and_chunks.append((letter, chunks))
                context = { 'letters_and_chunks': letters_and_chunks }
                output_xml = render_chunks(context)
                write_file(file_count, output_xml)
                n_chars = m
                chunks = [xml]
                file_count += 1
                letters_and_chunks = []
                letter = ''  # Обнуляем текущую букву, чтобы она не выводилась
                             # для следующей порции статей на ту же букву.
            else:
                n_chars += m
                chunks.append(xml)

        if isinstance(entry, Entry):
            ceq = entry.civil_equivalent
        elif isinstance(entry, dict):
            ceq = entry['referenced_lexemes'][0].civil_equivalent
        note = '%s [ %s%% ] %s\r' % (
                _letter,
                int(round(i / n_entries * 100)),
                ceq + ERASE_LINEEND)
        sys.stderr.write(note)
        sys.stderr.flush()

    if chunks:
        letters_and_chunks.append((letter, chunks))
    chunks = []
    if SPLIT_BY_LETTERS and letters_and_chunks:
        context = { 'letters_and_chunks': letters_and_chunks }
        output_xml = render_chunks(context)
        write_file(file_count, output_xml)
        file_count += 1
        n_chars = 0
        letters_and_chunks = []

if not SPLIT_BY_LETTERS:
    context = { 'letters_and_chunks': letters_and_chunks }
    output_xml = render_chunks(context)
    write_file(file_count, output_xml)

sys.stderr.write(ERASE_LINE)
print(SHOW_CURSOR, file=sys.stderr)

if len(entries1) < 7:
    for wordform, ref, entry in entries1:
        print('Antconc wf: "{}", UCS ref: "{}", Lexeme: "{}"'
              .format(wordform, ref, entry), file=sys.stderr)
    print(file=sys.stderr)

sys.exit(0)
