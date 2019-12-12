import re

from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import antconc_ucs8
from hip2unicode.conversions import antconc_ucs8_without_aspiration
from hip2unicode.conversions import antconc_civilrus
from hip2unicode.conversions import antconc_antconc_wo_titles

compiled_conversion_wo_titles = compile_conversion(
        antconc_antconc_wo_titles.conversion)
compiled_conversion_with_aspiration = compile_conversion(
        antconc_ucs8.conversion)
compiled_conversion_without_aspiration = compile_conversion(
        antconc_ucs8_without_aspiration.conversion)
compiled_conversion_civil = compile_conversion(antconc_civilrus.conversion)

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
