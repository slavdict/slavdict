import re

from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import antconc_ucs8
from hip2unicode.conversions import antconc_ucs8_corrupted_antconc
from hip2unicode.conversions import antconc_ucs8_without_aspiration
from hip2unicode.conversions import antconc_civilrus
from hip2unicode.conversions import antconc_antconc_wo_titles

compiled_conversion_antconc_anticorrupt = compile_conversion(
        antconc_ucs8_corrupted_antconc.conversion)
compiled_conversion_civil = compile_conversion(antconc_civilrus.conversion)
compiled_conversion_with_aspiration = compile_conversion(
        antconc_ucs8.conversion)
compiled_conversion_without_aspiration = compile_conversion(
        antconc_ucs8_without_aspiration.conversion)
compiled_conversion_wo_titles = compile_conversion(
        antconc_antconc_wo_titles.conversion)

def html_escape(text):
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    text = text.replace('"', '&#34;')
    return text.replace("'", '&#39;')

def html_unescape(text):
    text = text.replace('&#39;', "'")
    text = text.replace('&#34;', '"')
    text = text.replace('&gt;',  '>')
    text = text.replace('&lt;',  '<')
    return text.replace('&amp;', '&')

def resolve_titles(text):
    return convert(text, compiled_conversion_wo_titles)

def ucs_convert(text):
    return html_escape(convert(text, compiled_conversion_with_aspiration))

def antconc_anticorrupt(text):
    return convert(text, compiled_conversion_antconc_anticorrupt)


def ucs_convert_affix(text):
    """
    Функции передаётся строка, которая должна содержать строковую запись
    аффикса в свободной форме -- не важно с дефисом или без. Если начальный
    дефис есть, он отбрасывается. Всё оставшееся конвертируется из
    представления AntConc в UCS8 без расстановки придыханий перед начальными
    гласными.
    """
    if text:
        if text[0] == '-':
            text = text[1:]
        return html_escape(convert(text, compiled_conversion_without_aspiration))


def civilrus_convert(word):
    return convert(word, compiled_conversion_civil)

def convert_for_index(word):
    civil_word = civilrus_convert(resolve_titles(word)).lower()
    ix_word = re.sub(r'ъ[иы]', 'ы', civil_word)
    ix_word = re.sub(r'[ъ=]', '', ix_word)
    ix_word = re.sub(r'^(бе|во|в|и|ни|ра|чре|чере)з([кпстфхцчшщ])',
                     r'\1с\2', ix_word)
    return re.sub(r'[^а-щы-я]', '', ix_word)

def ucs_affix_or_word(atr):
    """
    Функция предназначенная для конвертации значения атрибута модели из
    представления AntConc в UCS8. Атрибут должен быть строкой. Если первым
    символом строки является дефис, то сам дефис отбрасывается, а конвертация
    производится без создания придыханий над начальными гласными из
    предположения, что это аффикс. Если первый символ -- не дефис, конвертация
    производится с созданием придыханий, подразумевается, что на вход подано
    слово, а не аффикс.

    Если входная строка пустая, то возвращается также пустая строка. Если
    непустая, то возвращается кортеж, где второй элемент -- это
    сконверированная строка, а первый -- булевская константа, указывающая,
    является ли строка аффиксом (True) или словом (False).

    Если данная функция используется в другой функции, то последней можно
    давать название с использованием аббревиатуры wax (Word or AffiX).

    Возможно, впоследствии лучше сделать, чтобы функция возвращала не кортеж,
    а объект. В качестве __str__ будет возвращаться сконвертированная
    строка, а информация о том, аффикс или нет, отдельным свойством.
    """
    if atr:
        if atr[0] == '-':
            return (True, ucs_convert_affix(atr[1:]))
        else:
            return (False, ucs_convert(atr))
    else:
        return atr

def several_wordforms(text):
    RE_COMMA = r'[,\s\(\)]+'
    words = re.split(RE_COMMA, text)
    return [(word, ucs_convert(word)) for word in words if word]

def levenshtein_distance(a, b):
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n, m)) space
        a, b = b, a
        n, m = m, n
    cur_row = list(range(n+1))  # Keep current and previous row, not entire matrix
    for i in range(1, m+1):
        pre_row, cur_row = cur_row, [i]+[0]*n
        for j in range(1, n+1):
            add, delete, change = pre_row[j]+1, cur_row[j-1]+1, pre_row[j-1]
            if a[j-1] != b[i-1]:
                change += 1
            cur_row[j] = min(add, delete, change)
    return cur_row[n]

def sort_key1(word):
    level1 = (
        (r"[='`\^\~А-ЯЄЅІЇѠѢѤѦѨѪѬѮѰѲѴѶѸѺѼѾ]", ''),
        ('ъ',      ''),
        ('аѵ',     'ав'),
        ('[еє]ѵ',  'ев'),
        ('ѯ',      'кс'),
        ('ѿ',      'от'),
        ('ѱ',      'пс'),

        ('а',      '00'),
        ('б',      '01'),
        ('в',      '02'),
        ('г',      '03'),
        ('д',      '04'),
        ('[еєѣ]',  '05'),
        ('ж',      '06'),
        ('[зѕ]',   '07'),
        ('[иіїѵ]', '08'),
        ('й',      '09'),
        ('к',      '10'),
        ('л',      '11'),
        ('м',      '12'),
        ('н',      '13'),
        ('[оѻѡѽ]', '14'),
        ('п',      '15'),
        ('р',      '16'),
        ('с',      '17'),
        ('т',      '18'),
        ('[уѹꙋ]',  '19'),
        ('[фѳ]',   '20'),
        ('х',      '21'),
        ('ц',      '22'),
        ('ч',      '23'),
        ('ш',      '24'),
        ('щ',      '25'),
        ('ы',      '26'),
        ('ь',      '27'),
        ('ю',      '28'),
        ('[ѧꙗ]',   '29'),
    )
    for pattern, substitution in level1:
        word = re.sub(pattern, substitution, word)
    return word

def sort_key2(word):
    level2 = (
        (r'=',     ''),
        (r"([аеє])(['`\^]?)ѵ", r'\g<1>\g<2>01'),

        (r"'",     '31'),
        (r"`",     '32'),
        (r"\^",    '33'),
        (r"\~",    '40'),
        (r"[А-ЩЫ-ЯЄЅІЇѠѢѤѦѨѪѬѮѰѲѴѶѸѺѼѾ]", '50'),

        ('Ъ',      '01'),
        ('ъ',      '02'),

        ('ѯ',      '0100'),
        ('ѱ',      '0100'),

        ('е',  '00'),
        ('є',  '01'),
        ('ѣ',  '02'),

        ('ѕ',  '01'),
        ('з',  '02'),

        ('и',    '00'),
        ('[ії]', '01'),
        ('ѵ',    '02'),

        ('о', '00'),
        ('ѻ', '01'),
        ('ѡ', '02'),
        ('ѿ', '0200'),
        ('ѽ', '03'),

        ('ѹ', '00'),
        ('ꙋ', '01'),
        ('у', '02'),

        ('ф', '00'),
        ('ѳ', '01'),

        ('ѧ', '00'),
        ('ꙗ', '01'),

        ('[а-я]', '00'),
    )
    for pattern, substitution in level2:
        word = re.sub(pattern, substitution, word)
    return word

def collogroup_sort_key(cg):
    text = ' '.join(c.collocation for c in cg.collocations)
    text = text.replace('-', '')
    text = re.sub(r'[\s/,\.;#\(\)]+', ' ', text)
    text = text.strip()
    text = resolve_titles(text)
    return [sort_key1(word) for word in text.split()]




def _aq(char_groups, optional=False):
    d = {}
    for chars in char_groups:
        for char in chars:
            chars_upper = chars.upper()
            if chars != chars_upper:
                pattern = '[{}{}]'.format(chars, chars_upper)
            else:
                pattern = '[{}]'.format(chars)
            if optional:
                pattern += '?'
            d[char] = pattern
            d[char.upper()] = pattern
    return d


def _bq(chars):
    d = {}
    for char in chars:
        upper_char = char.upper()
        pattern = '[{}{}]'.format(char, upper_char)
        d[char] = pattern
        d[upper_char] = pattern
    return d


def _dq(*pairs):
    multi, single = {}, {}
    for d, s in pairs:
        special_case = d == 'от'
        if special_case:
            first_char = 'оѡѻѽ'
            accent = "['`^]"
            oooo = '[{}]'.format(first_char)
            dargs = (oooo + 'т',  oooo.upper() + 'т', oooo.upper() + 'Т')
            dargs_accent = (oooo + accent + 'т',  oooo.upper() + accent + 'т',
                            oooo.upper() + accent + 'Т')
        else:
            first_char = d[0]
            dargs = d, d[0].upper() + d[1], d.upper()
        dpat = '{}|{}|{}'.format(*dargs)
        spat = '[{}{}]'.format(s, s.upper())
        if special_case:
            # Для лигатуры "от" всегда добавляем необязательное ударение
            spat = '[{}{}]'.format(s, s.upper()) + accent + '?'

            dpat_accent = '{}|{}|{}'.format(*dargs_accent)
            accent_pattern =  '({}|{})'.format(spat + accent, dpat_accent)
        pattern = '({}|{})'.format(spat, dpat)

        single[s] = pattern
        single[s.upper()] = pattern
        if special_case:
            for accent in "'`^":
                multi[s + accent] = accent_pattern
                multi[s.upper() + accent] = accent_pattern
        for char in first_char:
            if special_case:
                for accent in "'`^":
                    multi[char + accent + d[1]] = accent_pattern
                    multi[char.upper() + accent + d[1]] = accent_pattern
                    multi[(char + accent + d[1]).upper()] = accent_pattern
            else:
                multi[char + d[1]] = pattern
                multi[char.upper() + d[1]] = pattern
                multi[(char + d[1]).upper()] = pattern
    return multi, single


def _vq(*pairs):
    d = {}
    accent = "['`^]"
    for a, b in pairs:
        apattern, bpattern = a, b
        if len(a) > 1:
            apattern = '[{}]'.format(a)
        if len(b) > 1:
            bpattern = '[{}]'.format(b)
        pattern = '({}|{}|{})'.format(apattern + bpattern,
                                      apattern.upper() + bpattern,
                                      (apattern + bpattern).upper())
        accent_pattern = '({}|{}|{})'.format(
                apattern + accent + bpattern,
                apattern.upper() + accent + bpattern,
                (apattern + accent + bpattern).upper())
        for first in a:
            for second in b:
                d[first + second] = pattern
                d[first.upper() + second] = pattern
                d[(first + second).upper()] = pattern
                for acc in "'`^":
                    d[first + acc + second] = accent_pattern
                    d[first.upper() + acc + second] = accent_pattern
                    d[(first + acc + second).upper()] = accent_pattern
    return d


ACQ_SINGLE = _aq(['еєѣ', 'зѕ', 'иіѵ', 'оѡѻѽ', 'уѹꙋ', 'фѳ', 'ѧꙗ'],
                 optional=False)
ACQ_SINGLE.update(_aq(['ъь', "'`^"], optional=True))
ACQ_SINGLE.update(_bq('абвгджйклмнпрстхцчшщыю'))
_d, _s = _dq(('кс', 'ѯ'), ('пс', 'ѱ'), ('от', 'ѿ'))
ACQ_SINGLE.update(_s)

ACQ_MUL = _d
ACQ_MUL.update(_vq(('a', 'вѵ'), ('еє', 'вѵ')))

ACQ_FINAL = _aq(['йи'], optional=False)


def antconc_wordform_query(text):
    length = len(text)
    query = ''
    for i, char in enumerate(text):
        trichar = text[i:i+3]
        bichar = text[i:i+2]
        if i == length - 1 and char in ACQ_FINAL:
            query += ACQ_FINAL[char]
        elif trichar in ACQ_MUL:
            query += ACQ_MUL[trichar]
        elif bichar in ACQ_MUL:
            query += ACQ_MUL[bichar]
        elif char in ACQ_SINGLE:
            query += ACQ_SINGLE[char]
        else:
            query += char
    return query


QSTART = r'^\(\^\|\(\?\<\=(\\s|\[[^\]]+\])\)\)(.*)$'
QEND = r'^(.*)\(\?\=\[[^\]]+\]\)$'

def get_query_orterms(text):
    text = text.strip()
    if re.findall(QSTART, text):
        text = re.sub(QSTART, r'\2', text)
    if re.findall(QEND, text):
        text = re.sub(QEND, r'\1', text)
    # Снимаем внешние скобки, если они есть
    # и если они действительно окаймляющие.
    if text[:1] == '(' and text[-1:] == ')':
        level = 0
        last_ix = len(text) - 1
        for ix, c in enumerate(text):
            if c == '(':
                level += 1
            elif c == ')':
                level -= 1
            if level == 0:
                if ix < last_ix:
                    break
                else:
                    text = text[1:-1]
    # Разбиваем на OR-компоненты
    level = 0
    last_ix = len(text) - 1
    or_terms = []
    or_term = ''
    for ix, c in enumerate(text):
        if c == '(':
            level += 1
        elif c == ')':
            level -= 1
        elif c == '|' and level == 0:
            or_terms.append(or_term)
            or_term = ''
            continue
        or_term += c
    or_terms.append(or_term)
    # Избавляемся от пустых строк
    or_terms = list(filter(None, or_terms))
    return or_terms


def make_query_from_orterms(or_terms):
    if or_terms:
        return r'(^|(?<=\s))(%s)(?=[\s.,;:!])' % '|'.join(set(or_terms))
    return ''


ROMANS = (
    (1000, 'M', ''),
    (100,  'C', 'D'),
    (10,   'X', 'L'),
    (1,    'I', 'V'),
)

def arabic2roman(n):
    roman = '*' if n >= ROMANS[0][0] * (10 if ROMANS[0][2] else 4) else ''
    for i, (value, dig1, dig5) in enumerate(ROMANS):
        a = n % (value * 10) // value
        if a == 0:
            continue
        elif 0 < a < 4:
            roman += dig1 * a
        elif a == 4:
            roman += dig1 + dig5
        elif a == 5:
            roman += dig5
        elif 5 < a < 9:
            roman += dig5 + (dig1 * (a - 5))
        elif a == 9 and i > 0:
            _, dig10, _ = ROMANS[i - 1]
            roman += dig1 + dig10
    return roman

CIVIL_IN_CSL = 1
CSL_IN_CIVIL = 2

APPLY_TO_CSL = 1
APPLY_TO_CIVIL = 2

def apply_to_mixed(func, text, mixed_content_type=CIVIL_IN_CSL, apply_to=APPLY_TO_CSL):
    lst = text.split('##')
    for i, elem in enumerate(lst):
        if not elem:
            continue
        if (i % 2 == 0 and (CIVIL_IN_CSL and APPLY_TO_CSL
                or CSL_IN_CIVIL and APPLY_TO_CIVIL)
                or i % 2 == 1 and (CIVIL_IN_CSL and APPLY_TO_CIVIL
                or CSL_IN_CIVIL and APPLY_TO_CSL)):
            elem = func(elem)
            lst[i] = elem
    return '##'.join(lst)
