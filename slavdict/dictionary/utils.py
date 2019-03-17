# -*- coding: UTF-8 -*-
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
    text = text.replace(u'&', u'&amp;')
    text = text.replace(u'<', u'&lt;')
    text = text.replace(u'>', u'&gt;')
    text = text.replace(u'"', u'&#34;')
    return text.replace(u"'", u'&#39;')

def html_unescape(text):
    text = text.replace(u'&#39;', u"'")
    text = text.replace(u'&#34;', u'"')
    text = text.replace(u'&gt;',  u'>')
    text = text.replace(u'&lt;',  u'<')
    return text.replace(u'&amp;', u'&')

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
        if text[0] == u'-':
            text = text[1:]
        return html_escape(convert(text, compiled_conversion_without_aspiration))


def civilrus_convert(word):
    return convert(word, compiled_conversion_civil)

def convert_for_index(word):
    civil_word = civilrus_convert(resolve_titles(word)).lower()
    ix_word = re.sub(ur'ъ[иы]', u'ы', civil_word)
    ix_word = re.sub(ur'[ъ=]', u'', ix_word)
    ix_word = re.sub(ur'^(бе|во|в|и|ни|ра|чре|чере)з([кпстфхцчшщ])',
                     ur'\1с\2', ix_word)
    return re.sub(ur'[^а-щы-я]', u'', ix_word)

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
    а объект. В качестве __unicode__ будет возвращаться сконвертированная
    строка, а информация о том, аффикс или нет, отдельным свойством.
    """
    if atr:
        if atr[0] == u'-':
            return (True, ucs_convert_affix(atr[1:]))
        else:
            return (False, ucs_convert(atr))
    else:
        return atr

def levenshtein_distance(a, b):
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

def sort_key1(word):
    level1 = (
        (ur"[='`\^\~А-ЯЄЅІЇѠѢѤѦѨѪѬѮѰѲѴѶѸѺѼѾ]", u''),
        (u'ъ',      u''),
        (u'аѵ',     u'ав'),
        (u'[еє]ѵ',  u'ев'),
        (u'ѯ',      u'кс'),
        (u'ѿ',      u'от'),
        (u'ѱ',      u'пс'),

        (u'а',      u'00'),
        (u'б',      u'01'),
        (u'в',      u'02'),
        (u'г',      u'03'),
        (u'д',      u'04'),
        (u'[еєѣ]',  u'05'),
        (u'ж',      u'06'),
        (u'[зѕ]',   u'07'),
        (u'[иіїѵ]', u'08'),
        (u'й',      u'09'),
        (u'к',      u'10'),
        (u'л',      u'11'),
        (u'м',      u'12'),
        (u'н',      u'13'),
        (u'[оѻѡѽ]', u'14'),
        (u'п',      u'15'),
        (u'р',      u'16'),
        (u'с',      u'17'),
        (u'т',      u'18'),
        (u'[уѹꙋ]',  u'19'),
        (u'[фѳ]',   u'20'),
        (u'х',      u'21'),
        (u'ц',      u'22'),
        (u'ч',      u'23'),
        (u'ш',      u'24'),
        (u'щ',      u'25'),
        (u'ы',      u'26'),
        (u'ь',      u'27'),
        (u'ю',      u'28'),
        (u'[ѧꙗ]',   u'29'),
    )
    for pattern, substitution in level1:
        word = re.sub(pattern, substitution, word)
    return word

def sort_key2(word):
    level2 = (
        (ur'=',     u''),
        (ur"([аеє])(['`\^]?)ѵ", ur'\g<1>\g<2>01'),

        (ur"'",     u'31'),
        (ur"`",     u'32'),
        (ur"\^",    u'33'),
        (ur"\~",    u'40'),
        (ur"[А-ЩЫ-ЯЄЅІЇѠѢѤѦѨѪѬѮѰѲѴѶѸѺѼѾ]", u'50'),

        (u'Ъ',      u'01'),
        (u'ъ',      u'02'),

        (u'ѯ',      u'0100'),
        (u'ѱ',      u'0100'),

        (u'е',  u'00'),
        (u'є',  u'01'),
        (u'ѣ',  u'02'),

        (u'ѕ',  u'01'),
        (u'з',  u'02'),

        (u'и',    u'00'),
        (u'[ії]', u'01'),
        (u'ѵ',    u'02'),

        (u'о', u'00'),
        (u'ѻ', u'01'),
        (u'ѡ', u'02'),
        (u'ѿ', u'0200'),
        (u'ѽ', u'03'),

        (u'ѹ', u'00'),
        (u'ꙋ', u'01'),
        (u'у', u'02'),

        (u'ф', u'00'),
        (u'ѳ', u'01'),

        (u'ѧ', u'00'),
        (u'ꙗ', u'01'),

        (u'[а-я]', u'00'),
    )
    for pattern, substitution in level2:
        word = re.sub(pattern, substitution, word)
    return word

def collogroup_sort_key(cg):
    text = u' '.join(c.collocation for c in cg.collocations)
    text = text.replace(u'-', u'')
    text = re.sub(ur'[\s/,\.;#\(\)]+', u' ', text)
    text = text.strip()
    text = resolve_titles(text)
    return [sort_key1(word) for word in text.split()]
