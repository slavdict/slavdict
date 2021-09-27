"""
Библиотека шаблонных тегов.

В ней должно быть по меньшей мере два тега. Один наподобие {% spaceless %}.
Пока рабочее название {% trim %}. Если он указывается без параметров, то должен
работать на уровне разметки django, удаляя все пробельные пространства после
правой границы тегов -- %} и перед левой границей -- {%. При указании списка
параметров (произвольной длины) он должен будет удалять все пробельные
пространства после правой границы и перед левой границей тегов того типа
разметки, который присутствует в списке параметров. Например, {% trim 'django'
'html' %}...{% endtrim %} должно удалять все пробелы и на уровне разметки
django и на уровне html-разметки.

Параметры 'html', 'xhtml' и 'xml' предполагается сделать синонимами. {% trim
'xml' %}...{% endtrim %} должно действовать как настоящий тег {% spaceless %},
но только без его дифференциации пробелов между тегами и пробелов между тегом и
текстом (эти последние он не удаляет).

Второй необходимый тег -- тег, внутри которого пробельное пространство
удаляться не будет.  Например, {% cdata %}...{% endcdata %}. Название тега
взято из SGML, где CDATA является сокращением от Character Data и обозначает
особую часть SGML-документа (marked section), символы которой не обрабатываются
парсером, а выдаются как есть:

<![ CDATA [текст, не обрабатываемый парсером SGML]]>

В SGML есть также и другие типы частей документа, обрабатываемые специальным
образом (marked section). В частности, RCDATA -- Replaceable Character Data.
Это область документа наподобие CDATA, но где сущности (entities, в частности
character data entities, CDATA entities и т.д.) и символьные ссылки (character
references) заменяются на соответствующие им символы. Подробнее см. книгу
Martin Bryan, Web SGML and HTML 4.0 Explained.
[http://www.is-thought.co.uk/book/home.htm]

Можно также сделать, что при теге {% trim %} нельзя будет указывать параметр
'django'. Т.е. будет подразумеваться, что пробельное пространство до и после
границ тегов -- {{, {%, {# и }}, %}, #} -- будет удаляться всегда, а учёт тегов
второго уровня будет только при наличии параметров. Возможно также, что не
будет необходимости указывать больше одного параметра, потому что может не
потребоваться большая вложенность, чем одинарная. Правда, в HTML-разметке
возможны вкрапления CSS или JavaScript, поэтому надо будет ещё раз подумать.

Можно ещё добавить тег {% space %} в котором в качестве параметров можно будет
использовать стандартные управляющие последовательности вроде \t, \v, \r, \n.
\s предлагается использовать для обозначения пробела. Параметры могут иметь
такой вид: {% space \s4 \n \t2 %}. Это должно обозначать вставку строки из
четырёх пробелов, одного символа перевода строки и двух символов табуляции.
Или же параметр можно записывать в виде обычной питоновской строки:
{% space '    \n\t\t' %}. Или первый вариант, но в кавычках.

##########################################################################

В данный момент в модуле описано четыре тэга:

{% trim %} ... {% endtrim %} -- Парный тэг. Удаляет все пробелы между
x/html-тегами, а также x/html-тэгами и текстом.

{{ space }} -- Непарный вспомогательный тэг для использования внутри {% trim %}.
Гарантирует наличие единичного пробела, если только не будет перекрыт тэгом {% backspace %}.

{{ backspace }} -- Непарный вспомогательный тэг для использования внутри {% trim %},
когда нужно перекрыть {{ space }}. Удаляет перед собой любые пробельные пространства
до ближайшего текста или тэга. Пробельное пространство может в частности содержать
символьные ссылки &nbsp;

{{ punct }} -- Непарный вспомогательный тэг для использования внутри {% trim %}.
В том случае если текст внутри тэга кончается на знак препинания, гарантирует
наличие за ним пробела. К сожалению, пока его использование регулируется слишком
жесткими правилами. Его необходимо помещать *между* тэгами, в которых будет текст.
Помещать *внутрь* таких тегов его нельзя. Впоследствии его надо будет каким-то
образом переделать.

{{ ! }} -- Непарный вспомогательный тэг для использования внутри {% trim %}.
Мешает удалять пробелы вокруг x/html-тэгов.

{{ onlyDot }} -- Непарный вспомогательный тэг, позволяющий поставить точку,
только если перед ним нет точки или многоточия.

{{ emspace }} -- пробел длины em, U+2003.

{{ enspace }} -- пробел длины en, U+2002.

{{ nbsp }} -- неразрывный пробел, no-break space, U+00A0.

{{ nbhyphen }} -- non-breaking hyphen, U+2011.

{{ softhyphen }} -- soft hyphen, U+00AD.

{{ wj }}, {{ zwnbsp }} -- word joiner WJ = zero width no-break space ZWNBSP,
U+2060. В стандарте Юникод ZWNBSP это U+FEFF, который также используется как
BOM. Начиная с версии 3.2 использование позиции U+FEFF как ZWNBSP объявлено
устаревшим и в этой ф-ции надо использовать WJ (U+2060).

{{ newline }} -- конец абзаца и начало нового.

"""
import collections
import re
from itertools import chain
from itertools import zip_longest
from itertools import starmap

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.utils.encoding import force_str
from django.utils.functional import keep_lazy_text

from jinja2 import nodes
from jinja2.ext import Extension

from slavdict.dictionary.utils import ucs_convert, html_escape, html_unescape
from .hyphenation import hyphenate_ucs8

additional_jinja_filters = {}
def register_filter(arg):
    if callable(arg):
        # arg -- функция с реализацией нового фильтра для jinja2
        additional_jinja_filters[arg.__name__] = arg
        return arg
    else:
        # arg -- имя, под которым нужно зарегистрировать функцию
        # с реализацией нового фильтра для jinja2
        def wrapper(func):
            additional_jinja_filters[arg] = func
            return func
        return wrapper

SLASH = '/'
ZWS = '\u200B'

# Специальные двойники нормальных символов, используемые для
# контроля за пробельным пространством
BACKSPACE = '\u0008'
EMSPACE = '\uE003'
ENSPACE = '\uE002'
EXCLAM = '\u1991'
NBSP = '\uEEA0'
NEWLINE = '\uEEEE'
ONLYDOT = '\u1902'
PUNCT = '\u1900'
SPACE = '\u0007'
SPACES = SPACE + EMSPACE + ENSPACE + NBSP + NEWLINE

@keep_lazy_text
def strip_spaces_between_tags_and_text(value):
    value = re.sub(r'>\s+', '>', force_str(value.strip()))
    value = re.sub(r'\s+<', '<', value)
    # {{ backspace }}
    # Звёздочка вместо плюса нужна, чтобы backspace'ы были удалены
    # в любом случае независимо от того, предшествует им пробел или нет.
    value = re.sub(r'([\s{spaces}]|&nbsp;)*{backspace}'.format(
                           spaces=SPACES, backspace=BACKSPACE), '', value)
    # {{ punct }}
    value = re.sub(PUNCT + r'(<[^>]+>)([\.,:;\!\?])', r'\1\2', value)
    value = re.sub(PUNCT, ' ', value)
    # {{ ! }}
    value = re.sub(EXCLAM, '', value)
    # {{ onlyDot }}
    value = re.sub(r'([\.…])((\s)|(&nbsp;))*' + ONLYDOT, r'\1', value)
    value = re.sub(r'((\s)|(&nbsp;))*' + ONLYDOT, r'.', value)
    # {{ newline }}
    value = re.sub(NEWLINE, '\n', value)
    # {{ nbsp }}
    value = re.sub(NBSP, '\u00A0', value)
    # {{ emspace }}
    value = re.sub(EMSPACE, '\u2003', value)
    # {{ enspace }}
    value = re.sub(ENSPACE, '\u2003', value)
    # {{ space }}
    value = re.sub(SPACE, ' ', value)
    return value

class TrimExtension(Extension):

    tags = {'trim'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        body = parser.parse_statements(['name:endtrim'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_strip_spaces'),
                               [], [], body).set_lineno(lineno)

    def _strip_spaces(self, caller=None):
        return strip_spaces_between_tags_and_text(caller().strip())

    def preprocess(self, source, name, filename=None):
        source = re.sub(r'{{\s*space\s*}}', SPACE, source)
        source = re.sub(r'{{\s*backspace\s*}}', BACKSPACE, source)
        source = re.sub(r'{{\s*punct\s*}}', PUNCT, source)
        source = re.sub(r'{{\s*!\s*}}', EXCLAM, source)
        source = re.sub(r'{{\s*onlyDot\s*}}', ONLYDOT, source)
        source = re.sub(r'{{\s*nbsp\s*}}', NBSP, source)
        source = re.sub(r'{{\s*newline\s*}}', NEWLINE, source)

        # {{ emspace }}, {{ enspace }}
        source = re.sub(r'{{\s*emspace\s*}}', EMSPACE, source)
        source = re.sub(r'{{\s*enspace\s*}}', ENSPACE, source)

        # {{ nbhyphen }}
        source = re.sub(r'{{\s*nbhyphen\s*}}', '\u2011', source)
        # {{ softhyphen }}
        source = re.sub(r'{{\s*softhyphen\s*}}', '\u00AD', source)
        # {{ wj }}, {{ zwnbsp }}
        source = re.sub(r'{{\s*wj\s*}}', '\u2060', source)
        source = re.sub(r'{{\s*zwnbsp\s*}}', '\u2060', source)
        return source

trim = TrimExtension

def cslav_nobr_words(value):
    """ Все слова в переданном тексте делает неразрывными, чтобы браузер их
    случайно не порвал посередине. Все многоточия, скобки и косые черты
    помечает для отображения гражданской графикой, а остальное --
    церковнославянской.

    """
    # многоточие, круглые, квадратные скобки и косая черта
    value = re.sub(r'(\.\.\.|[\(\)\[\]/])', r'<span>\1</span>', value)
    pattern = '<span class="cslav nobr">%s</span>'
    words = (pattern % word for word in value.split())
    return '&#32;'.join(words)


SCRIPT_CSLAV = 'cslav'
SCRIPT_CIVIL = 'civil'

class Tag(object):
    TAG_IND = '<x aid:cstyle="{}">%s</x>'
    TAG_WEB = '<span class="{}">%s</span>'
    NO_TAG = '%s'

    def __init__(self, cslav_style=None, civil_style=None, for_web=False):
        self.cslav_style = cslav_style
        self.civil_style = civil_style
        self.for_web = for_web

    def get_tag(self, output_script):
        if output_script == SCRIPT_CSLAV:
            style = self.cslav_style
        elif output_script == SCRIPT_CIVIL:
            style = self.civil_style
        else:
            style = None
        if style is None:
            return self.NO_TAG
        if self.for_web:
            return self.TAG_WEB.format(style)
        else:
            return self.TAG_IND.format(style)

NON_SOFT_HYPHENS = ('-', '\u2010', '\u2011')

class Segment(Tag):
    TYPE_WORD = 'word'
    TYPE_WORD_WITH_HYPHEN = 'word_with_hyphen'
    TYPE_PERIOD = 'period'
    TYPE_ELLIPSIS = 'ellipsis'
    TYPE_COMMA = 'comma'
    TYPE_COLON = 'colon'
    TYPE_SEMICOLON = 'semicolon'
    TYPE_EXCL = 'exclamation'
    TYPE_LEFT_QUOTE = 'left_quote'
    TYPE_RIGHT_QUOTE = 'right_quote'
    TYPE_QUOTE = 'quote'
    TYPE_KAVYKA = 'kavyka'
    TYPE_LEFT_BRACKET = 'left_bracket'
    TYPE_RIGHT_BRACKET = 'right_bracket'
    TYPE_ASTERISK = 'asterisk'
    TYPE_DASH = 'dash'
    TYPE_SPACE = 'space'
    TYPE_HYPHEN = 'hyphen'
    TYPE_SLASH = 'slash'
    TYPE_EXTERNAL = 'external'

    TYPES_LEFT_PAIRING = (TYPE_LEFT_BRACKET, TYPE_LEFT_QUOTE)
    TYPES_RIGHT_PAIRING = (TYPE_RIGHT_BRACKET, TYPE_RIGHT_QUOTE)
    TYPES_PAIRING = (TYPE_QUOTE, TYPE_KAVYKA)
    TYPES_SEPARATORS = (TYPE_ASTERISK, TYPE_DASH, TYPE_SPACE)
    TYPES_ADHERING_SEPARATORS = (TYPE_PERIOD, TYPE_ELLIPSIS, TYPE_COMMA,
                                 TYPE_COLON, TYPE_SEMICOLON, TYPE_EXCL)

    def __init__(self, segment, tag, base_script=SCRIPT_CSLAV):
        self.segment = segment
        self.tag = tag
        self.base_script = base_script
        self.output_script = base_script

        if self.segment == '...' or \
                self.segment == '…' and self.base_script == SCRIPT_CIVIL:
            self.type = self.TYPE_ELLIPSIS
            self.output_script = SCRIPT_CIVIL
            self.segment = '…'

        elif self.segment == '.':
            self.type = self.TYPE_PERIOD

        elif self.segment == ',':
            self.type = self.TYPE_COMMA

        elif self.segment == ':':
            self.type = self.TYPE_COLON

        elif self.segment == ';':
            self.type = self.TYPE_SEMICOLON

        elif self.segment == '!':
            self.type = self.TYPE_EXCL

        elif self.segment == '«':
            self.type = self.TYPE_LEFT_QUOTE

        elif self.segment == '»':
            self.type = self.TYPE_RIGHT_QUOTE

        elif self.segment in list('“”„"‘’‛\''):
            self.type = self.TYPE_QUOTE
            self.output_script = SCRIPT_CIVIL

        elif self.segment == '°' and self.base_script == SCRIPT_CSLAV:
            self.type = self.TYPE_KAVYKA
            self.output_script = SCRIPT_CSLAV

        elif self.segment == '*':
            self.type = self.TYPE_ASTERISK

        elif self.segment in list('([\u27e8'):
            self.type = self.TYPE_LEFT_BRACKET
            self.output_script = SCRIPT_CIVIL

        elif re.findall('\u27e8=\s*', self.segment):
            # Угловая скобка со знаком равно в примерах
            self.type = self.TYPE_LEFT_BRACKET
            self.output_script = SCRIPT_CIVIL
            self.segment = '\u27e8=' + NBSP

        elif self.segment in list(')]\u27e9'):
            self.type = self.TYPE_RIGHT_BRACKET
            self.output_script = SCRIPT_CIVIL

        elif self.segment in ('/', '/' + ZWS):
            self.segment = '/' + ZWS
            self.type = self.TYPE_SLASH
            self.output_script = SCRIPT_CIVIL

        elif self.segment.isspace():
            self.type = self.TYPE_SPACE
            self.output_script = SCRIPT_CIVIL
            if '\u00a0' in self.segment:
                self.segment = NBSP
            elif '\u2003' in self.segment:
                self.segment = EMSPACE
            elif '\u2002' in self.segment:
                self.segment = ENSPACE
            else:
                self.segment = SPACE

        elif self.segment in ('\u2013', '\u2014'):
            self.type = self.TYPE_DASH
            self.output_script = SCRIPT_CIVIL

        elif self.segment in NON_SOFT_HYPHENS:
            self.type = self.TYPE_HYPHEN
            self.output_script = SCRIPT_CIVIL

        else:
            if any(hyphen in self.segment for hyphen in NON_SOFT_HYPHENS):
                self.type = self.TYPE_WORD_WITH_HYPHEN
            self.type = self.TYPE_WORD

    def _get_word_markup_string(self, seg):
        segment = html_escape(hyphenate_ucs8(seg))

        RE_NON_UCS8_LETTER_TITLES = '(?<!^)([МТ])'
        if self.base_script == SCRIPT_CSLAV and \
                re.findall(RE_NON_UCS8_LETTER_TITLES, segment):
            if self.tag.for_web:
                tag_template = '<span class="CSLSuper">%s</span>'
            else:
                tag_template = '<x aid:cstyle="CSLSuper">%s</x>'
            parts = re.split(RE_NON_UCS8_LETTER_TITLES, segment)
            parts = [tag_template % p.lower() if i % 2 else p
                     for i, p in enumerate(parts)]
            segment = ''.join(parts)

        RE_ASCENDER_WITH_DIA = '([эt])([12345])'  # UCS8-символы для ять, от и
                                                  # диакритики.
        # Известные случаи:
        #
        #   - ять + придыхание (см. статью "еждение").
        #   - ять + придыхание + акут (см. статьи "ехати", "ездити").
        #   - от + акут (см. пример "отграда" в статье "византия")
        #
        if self.base_script == SCRIPT_CSLAV and \
                re.findall(RE_ASCENDER_WITH_DIA, segment):
            if self.tag.for_web:
                tag1_template = '<span class="UCS8Ascender">%s</span>'
                tag2_template = '<span class="UCS8DiaByAscender">%s</span>'
            else:
                tag1_template = '<x aid:cstyle="UCS8Ascender">%s</x>'
                tag2_template = '<x aid:cstyle="UCS8DiaByAscender">%s</x>'
            parts = re.split(RE_ASCENDER_WITH_DIA, segment)
            parts = [{
                        1: tag1_template % p,
                        2: tag2_template % p,
                        0: p }[i % 3]
                     for i, p in enumerate(parts)]
            segment = ''.join(parts)

        # NOTE: Между вставкой мягких переносов (``hyphenate_ucs8``) и их
        # стилизацией необходима фаза расстановки буквенных титл для М и Т.
        # Если последовательность этапов нарушить, то буквенные титла будут
        # расставляться неправильно.
        if self.tag.for_web:
            HYPHEN_TAG = '<span class="Text">\u00AD</span>'
            segment = HYPHEN_TAG.join(
                    '<span class="nobr">%s</span>' % part
                    for part in segment.split('\u00AD'))
        else:
            HYPHEN_TAG = '<h aid:cstyle="Text">\u00AD</h>'
            segment = segment.replace('\u00AD', HYPHEN_TAG)

        return segment

    def __str__(self):
        tag = self.tag.get_tag(self.output_script)
        if self.type == self.TYPE_EXTERNAL:
            segment = self.segment
        elif self.type in (self.TYPE_WORD, self.TYPE_WORD_WITH_HYPHEN):
            if self.output_script == SCRIPT_CSLAV:
                segs = re.split('([%s]+)' % ''.join(NON_SOFT_HYPHENS),
                                self.segment)
                txt = ''
                for i, seg in enumerate(segs):
                    if i % 2 == 0:
                        segment = self._get_word_markup_string(seg)
                        tag = self.tag.get_tag(self.output_script)
                    else:
                        segment = html_escape(seg)
                        tag = self.tag.get_tag(SCRIPT_CIVIL)
                    txt += tag % segment
                return txt
            else:
                segment = self._get_word_markup_string(self.segment)
        else:
            segment = html_escape(self.segment)
            angle_brackets = re.split('([\u27e8\u27e9])', segment)
            if self.tag.for_web:
                tag_template = '<span class="angleBracket">%s</span>'
            else:
                tag_template = '<x aid:cstyle="angleBracket">%s</x>'
            segment = ''.join(
                tag_template % item if i % 2 == 1 else item
                for i, item in enumerate(angle_brackets)
            )
        return tag % segment

class ExternalSegment(Segment):
    def __init__(self, segment, tag, base_script=SCRIPT_CIVIL):
        self.segment = segment
        self.tag = tag
        self.base_script = base_script
        self.output_script = base_script
        self.type = Segment.TYPE_EXTERNAL


RE_CSLAV_SEGMENT = re.compile('(%s)' % '|'.join([
        r'\.\.\.',
        r'[\(\)\[\]\.,;:!«»“”„"‘’‛\'—–\-\*°'
            '\u2011\u2010]',
        '\u27e8=['
            r'\s'
            '\u00a0]*',  # Открывающая угловая скобка со знаком равно
        r'\/{0}?'.format(ZWS),
        r'[\s'
            '\u00a0]+']))
RE_CIVIL_SEGMENT = re.compile('(%s)' % '|'.join([
        r'\.\.\.',
        r'[\(\)\[\]\.,;:!?…\\/«»“”„"‘’‛\'—–\-\*'
            '\u2011\u2010]',
        r'\/{0}?'.format(ZWS),
        r'[\s'
            '\u00a0]+']))

def get_nonword_segments(string, tag, base_script):
    if base_script == SCRIPT_CSLAV:
        regexp = RE_CSLAV_SEGMENT
    elif base_script == SCRIPT_CIVIL:
        regexp = RE_CIVIL_SEGMENT
    else:
        raise NotImplementedError
    segments = [Segment(s, tag)
                for s in re.split(regexp, string)
                if s]  # Исключаем сегменты, состоящие из пустых строк
    return segments

class Word(object):
    def __init__(self, words, index):
        assert isinstance(words, Words)
        assert 0 <= index < len(words.words)
        self.word = words.words[index]
        self.left_in_between = words.in_betweens[index]
        self.right_in_between = words.in_betweens[index + 1]

class Words(object):
    def __init__(self):
        self.words = []
        self.in_betweens = [[]]

    def add(self, item):
        if not item:
            return
        elif isinstance(item, Words):
            self.words.extend(item.words)
            self.in_betweens[-1] += item.in_betweens[0]
            self.in_betweens.extend(item.in_betweens[1:])
        elif isinstance(item, Segment):
            if item.type in (Segment.TYPE_WORD, Segment.TYPE_WORD_WITH_HYPHEN):
                self.words.append(item)
                self.in_betweens.append([])
            else:
                self.in_betweens[-1].append(item)
        elif isinstance(item, collections.Sequence) and \
                not isinstance(item, str):
            assert all(isinstance(x, Segment) for x in item)
            for s in item:
                if s.type in (Segment.TYPE_WORD, Segment.TYPE_WORD_WITH_HYPHEN):
                    self.words.append(s)
                    self.in_betweens.append([])
                else:
                    self.in_betweens[-1].append(s)
        else:
            raise TypeError

    def __getitem__(self, index):
        return Word(self, index)

    def __len__(self):
        return len(self.words)

    def __iter__(self):
        ''' Итератор последовательно возвращает объекты Segment '''
        def f(in_between, word):
            if word is None:
                return in_between
            return list(in_between) + [word]
        return chain(*starmap(f, zip_longest(self.in_betweens, self.words)))

    def __str__(self):
        return ''.join(str(s) for s in self)


CSL_CSTYLE = 'CSLSegment'
TEXT_CSTYLE = 'Text'
EM_CSTYLE = 'Em'
VALENCY_CSTYLE = 'Valency'

# NOTE: скобки, окаймляющие регулярное выражение, нельзя опустить, т.к. нужно,
# чтобы при разбивке с помощью split в списке сохранялись не только слова, но
# и все символы между словами. В полученном списке должно быть нечетное число
# элементов.
RE_CSLAV_SPLIT = (
    r'((?:'
    '\u27e8=?|\u27e9|'
    r'[\s'
    '\u00a0'
    r'.,;:!/«»“”„"‘’‛\'—–\-'
    '\u2011\u2010'
    r'*°\(\)\[\]]'
    r')+)'
)
RE_CIVIL_SPLIT = (
    r'('
    r'[\s'
    '\u00a0'
    r'.…,;:!?\\/«»“”„"‘’‛\'—–\-'
    '\u2011\u2010'
    r'*\(\)\[\]]+'
    r')'
)
HYPHEN = '-'

def get_word_even_with_hyphen(index, segments, n_segments):
    word = segments[index]
    while index + 1 < n_segments and any(hyphen == segments[index + 1]
                                     for hyphen in NON_SOFT_HYPHENS):
        word += segments[index + 1]
        index += 2
        if index < n_segments:
            word += segments[index]
    index += 1
    return (word, index)

def cslav_words(value, cstyle=CSL_CSTYLE, civil_cstyle=None, for_web=False):
    """ Аналог cslav_nobr_words для импорта в InDesign. """
    if value is None:
        value = ''
    value = html_unescape(value)
    tag = Tag(cslav_style=cstyle, civil_style=civil_cstyle, for_web=for_web)
    segments = re.split(RE_CSLAV_SPLIT, value)

    words = Words()
    n_segments = len(segments)
    for i in range(n_segments // 2 + 1):
        s1 = i * 2
        # Пропускаем сегменты, являющиеся частями слов, содержащих дефисы
        if (s1 - 1 >= 0 and any(hyphen == segments[s1 - 1]
                                for hyphen in NON_SOFT_HYPHENS)):
            continue
        word_segment, s2 = get_word_even_with_hyphen(s1, segments, n_segments)
        word = Segment(word_segment, tag)
        if s2 < len(segments):
            in_between = get_nonword_segments(segments[s2], tag, SCRIPT_CSLAV)
        else:
            in_between = []
        if word == '' and s1 == 0:  # Если первое слово является пустым
            words.add(in_between)
        elif word == '' and s2 == len(segments):  # Если последнее слово пустое
            break
        else:
            words.add(word)
            words.add(in_between)
    #if list(words)[0].segment.startswith('мин'):
    #    for w in words:  # Отладочная печать
    #        print('%s: "%s"' % (w.type, w.segment))
    return words

def civil_words(value, civil_cstyle=None, for_web=False):
    if value is None:
        value = ''
    value = html_unescape(value)
    tag = Tag(cslav_style=None, civil_style=civil_cstyle, for_web=for_web)

    segments = re.split(RE_CIVIL_SPLIT, value)
    words = Words()
    for i in range(len(segments) // 2 + 1):
        s1 = i * 2
        s2 = s1 + 1
        word = Segment(segments[s1], tag, base_script=SCRIPT_CIVIL)
        if s2 < len(segments):
            in_between = get_nonword_segments(segments[s2], tag, SCRIPT_CIVIL)
        else:
            in_between = []
        if word == '' and s1 == 0:  # Если первое слово является пустым
            words.add(in_between)
        elif word == '' and s2 == len(segments):  # Если последнее слово пустое
            break
        else:
            words.add(word)
            words.add(in_between)
    return words

def _prepare_translation_data(data, n):
    if not data:
        return {}

    sortfunc = lambda t: (t.fragment_end, t.order, t.id)
    for index in list(data.keys()):
        translations = data[index]
        if index > n:
            data[n].extend(translations)
            del data[index]
        else:
            translations.sort(key=sortfunc)
    translations = data[n]
    translations.sort(key=sortfunc)

    return data

def _insert_translation_data(words, data, show_additional_info=False,
                             hidden_data=None):
    for_web = words[0].word.tag.for_web
    if hidden_data is None or not show_additional_info or not for_web:
        hidden_data = {}  # В InDesign комментарии авторов не нужны
    if for_web:
        cstyle = 'Text hyphenate'
    else:
        cstyle = 'Text'
    tag0 = Tag(cslav_style=None, civil_style='Text', for_web=for_web)
    tag1 = Tag(cslav_style=None, civil_style=cstyle, for_web=for_web)
    if show_additional_info:
        cstyle2 = 'ai ai-grfex ' + cstyle
        tag2 = Tag(cslav_style=None, civil_style=cstyle2, for_web=for_web)

    ai = ' <span class="ai ai-grfex Text hyphenate">%s</span>'
    process_translation = lambda translation, for_web: ind_regex(
            html_escape(translation),
            'Em', r'(?<![А-Яа-я])букв\.', for_web=for_web)
    c = lambda t: (show_additional_info and t.additional_info.strip()
            and for_web)
    def tt(translation):
        if not translation.source:
            return '‘%s’%s'
        source_mark = ExternalSegment(translation.source_label() + SPACE,
                Tag(cslav_style=None, civil_style='Em', for_web=for_web))
        return '{0}%s%s'.format(source_mark)

    # Расстановка частичных переводов, отображаемых в статье
    for index, lst in list(data.items()):
        if not lst:
            continue
        translations = []
        for t in lst:
            ai_text = (ai % html_escape(t.additional_info)) if c(t) else ''
            t_text = process_translation(t.translation, for_web)
            translation = tt(t) % (t_text, ai_text)
            if for_web:
                translation = '%s%s' % (
                    '<span class="anchor"><a id="%s"></a></span>' %
                        t.get_url_fragment(),
                    translation)
            translations.append(translation)
        translations = ',&#32;'.join(translations)
        translations = '(%s)' % translations
        seg = ExternalSegment(translations, tag1, SCRIPT_CIVIL)
        space = Segment(' ', tag0, SCRIPT_CIVIL)
        words[index - 1].right_in_between[:0] = [space, seg]

    # Расстановка частичных переводов, отображаемых в авторских комментах
    for index, lst in list(hidden_data.items()):
        if not lst:
            continue
        translations = []
        for t in lst:
            t_text = html_escape(t.translation)
            ai_text = ('&#32;[%s]' % html_escape(t.additional_info)) if c(t) else ''
            translations.append(tt(t) % (t_text, ai_text))
        translations = ',&#32;'.join(translations)
        seg = ExternalSegment(translations, tag2, SCRIPT_CIVIL)
        space = Segment(' ', tag0, SCRIPT_CIVIL)
        right_in_between = words[index - 1].right_in_between
        x = [s.type == Segment.TYPE_EXTERNAL for s in right_in_between]
        if True in x:
            ix = x.index(True) + 1
        else:
            ix = 0
        right_in_between[ix:ix] = [space, seg]
    return words

@register_filter
def insert_translations(words, data, show_additional_info=False, hidden_data=None):
    data = _prepare_translation_data(data, len(words))
    if show_additional_info:
        hidden_data = _prepare_translation_data(hidden_data, len(words))
    else:
        hidden_data = None
    words = _insert_translation_data(words, data, show_additional_info, hidden_data)
    return words

def cslav_subst(x):
    return EXCLAM + cslav_nobr_words(ucs_convert(x.group(1))) + EXCLAM

@register_filter
def cslav_injection(value):
    """ Заменяет текст вида ``## <text::antconc> ##`` на ``<text::ucs8>``.
    """
    value = re.sub(r'##(.*?)##', cslav_subst, value)
    return value

def subst_func(func):
    def f(match):
        x, y, z = match.group(1), match.group(2), match.group(3)
        if '\u00a0' in x:
            x = NBSP
        elif ' ' in x:
            x = SPACE
        if '\u00a0' in z:
            z = NBSP
        elif ' ' in z:
            z = SPACE
        return '%s%s%s' % (x, func(y), z)
    return f

@register_filter
def ind_cslav_injection(value, cstyle=CSL_CSTYLE, for_web=False):
    """ Заменяет текст вида ``## <text::antconc> ##`` на ``<text::ucs8>``.
    """
    ind_cslav = subst_func(lambda x: cslav_words(
        ucs_convert(x), cstyle, for_web=for_web))
    return re.sub(r'(\s*)##(.*?)##(\s*)', ind_cslav, value)

@register_filter
def web_cslav_injection(value, cstyle=CSL_CSTYLE):
    return ind_cslav_injection(value, cstyle, for_web=True)

@register_filter
def ind_civil_injection(value, civil_cstyle, cslav_cstyle=CSL_CSTYLE,
        civil2_cstyle=None, for_web=False):
    words = Words()
    for i, elem in enumerate(value.split('##')):
        if not elem:
            continue
        if i % 2:
            words2 = civil_words(elem, civil_cstyle, for_web)
        else:
            words2 = cslav_words(elem, cslav_cstyle, civil2_cstyle, for_web)
        words.add(words2)
    return words

@register_filter
def web_civil_injection(value, civil_cstyle, cslav_cstyle=CSL_CSTYLE,
        civil2_cstyle=None):
    return ind_civil_injection(value, civil_cstyle, cslav_cstyle,
                               civil2_cstyle, for_web=True)

@register_filter
def ind_regex(value, cstyle, regex, for_web=False):
    """ Помечает указанным стилем cstyle найденный текст
    """
    tag = Tag(cslav_style=None, civil_style=cstyle, for_web=for_web)
    _ind_regex = subst_func(lambda x: Segment(x, tag, base_script=SCRIPT_CIVIL))
    return re.sub(r'(\s*)(%s)(\s*)' % regex, _ind_regex, value)

@register_filter
def web_regex(value, cstyle, regex):
    return ind_regex(value, cstyle, regex, for_web=True)

def subst_headword_func(func1, func2, headword):
    def f(match):
        if match.group(7) == match.group(9) == '##':
            print('::0', match.group())
            x, y, z = match.group(6), match.group(8), match.group(10)
            f = func2(y)
            print('::1', f)
        elif match.group(2) == '{' and match.group(4) == '}':
            x, y, z = match.group(1), match.group(3), match.group(5)
            f = func1(y, headword)
        else:
            raise RuntimeError
        if '\u00a0' in x:
            x = NBSP
        elif ' ' in x:
            x = SPACE
        if '\u00a0' in z:
            z = NBSP
        elif ' ' in z:
            z = SPACE
        return '%s%s%s' % (x, f, z)
    return f

def headword_injection(value, headword, cslav_cstyle=CSL_CSTYLE, for_web=False):
    if not value.strip():
        return cslav_words(ucs_convert(headword), cslav_cstyle, for_web=for_web)
    else:
        return cslav_words(ucs_convert(value), cslav_cstyle, for_web=for_web)

@register_filter
def ind_valency(value, headword,
        cslav_cstyle=CSL_CSTYLE, text_cstyle=TEXT_CSTYLE,
        em_cstyle=EM_CSTYLE, valency_cstyle=VALENCY_CSTYLE, for_web=False):
    """ Создает текст модели управления лексемы.

    На место фигурных скобок подставляется основной вариант написания лексемы,
    если в фигурных скобках текст отсутствует. Например, для лексемы ``ради``
    последовательность:

      кого-л./чего-л. {}

    будет изменена на ``кого-л./чего-л. ради``.

    Если текст в фигурных скобках присутствует, то он используется вместо
    основного варианта написания лексемы, которую необходимо использовать в
    модели управления:

      кто-л. {имену'ется} кто-л.

    """
    hwfunc = lambda x, hw: headword_injection(x, hw, cslav_cstyle, for_web=for_web)
    cswfunc = lambda x: cslav_words(ucs_convert(x), cslav_cstyle, for_web=for_web)
    ind_headword = subst_headword_func(hwfunc, cswfunc, headword)
    tag = Tag(cslav_style=None, civil_style=text_cstyle, for_web=for_web)
    joiner = '%s%s' % (Segment(';', tag), SPACE)
    frames = []
    for frame in value.split(';'):
        frame = re.sub(r'(?:(\s*)(\{)(.*?)(\})(\s*)|(\s*)(##)(.*?)(##)(\s*))',
                       ind_headword, frame.strip())
        frame = ind_regex(frame,
                valency_cstyle, '[а-яё]+[\\-\u2011]л\\.', for_web=for_web)
        frame = ind_regex(frame,
                em_cstyle, 'с\\sдвойн\\.\\s(?:им|вин)\\.|'
                           'с\\sинф\\.|с\\sпридат\\.|с\\sпрямой\\sречью',
                for_web=for_web)
        frames.append(frame)
    return joiner.join(frames)

@register_filter
def web_valency(value, headword,
        cslav_cstyle=CSL_CSTYLE, text_cstyle=TEXT_CSTYLE,
        em_cstyle=EM_CSTYLE, valency_cstyle=VALENCY_CSTYLE):
    return ind_valency(value, headword,
        cslav_cstyle=cslav_cstyle, text_cstyle=text_cstyle,
        em_cstyle=em_cstyle, valency_cstyle=valency_cstyle, for_web=True)

@register_filter
def web_href(value, regex, href):
    """ Делает из текста regex гиперссылку """
    tag = '<a href="{href}" target="_blank" class="hash2">%s</a>'.format(href=href)
    _href = subst_func(lambda x: tag % x)
    return re.sub(r'(\s*)(%s)(\s*)' % regex, _href, value)


RE_FIND_REF = (
    r'\s*'                      # <Начальные пробелы>
    r'(?:idem|cf|qv|ref)'       # <Тип ссылки>
    r'(?:'
        r'\['
            r'\s*[а-яА-Я]+'     # <Гражданское написание заглавного слова>
            r'\s*[1-9]?'        # <Номер омонима>
            r'(?:\s*-\s*'       # <Список значений>
                r'\d+(?:\s*,\s*\d+)*'
            r')?\s*'
        r'\]'
    r')+'
    r'(?:'
        r'\{'
            r'[^\{\}]*'         # <Текст-разделитель>
        r'\}'
    r')*'
    r'\s*'                      # <Конечные пробелы>
)
RE_PARSE_REF = (
    r'(\s*)'                # <Начальные пробелы>
    r'(idem|cf|qv|ref)'     # <Тип ссылки>
    r'((?:'
        r'\['
            r'[^\[\]]+'     # <Все статьи и значения>
        r'\]'
    r')+)'
    r'((?:'
        r'\{'
            r'[^\{\}]*'     # <Все разделители>
        r'\}'
    r')*)'
    r'(\s*)'                # <Конечные пробелы>
)

RE_PARSE_REF_ENTRY = (
    r'\s*([а-яА-Я]+)'   # <Гражданское написание заглавного слова>
    r'\s*([1-9])?'      # <Номер омонима>
    r'(?:\s*-\s*'       # <Список значений>
        r'(\d+(?:\s*,\s*\d+)*)'
    r')?\s*'
)

def insert_ref(x, for_web, ref_func=None):
    em_tag = Tag(cslav_style=None, civil_style='Em', for_web=for_web)
    text_tag = Tag(cslav_style=None, civil_style='Text', for_web=for_web)
    number_tag = Tag(cslav_style=None, civil_style='HomonymNumber',
                     for_web=for_web)
    csl_tag = Tag(cslav_style='CSLSegment', civil_style=None, for_web=for_web)

    text = ''
    s1, ref, ents, seps, s2 = re.findall(RE_PARSE_REF, x, re.IGNORECASE)[0]

    ref = ref.lower()
    if ref == 'idem':
        s = Segment('то же, что', text_tag, base_script=SCRIPT_CIVIL)
        text += '%s%s' % (s, SPACE)
    elif ref == 'cf':
        s = Segment('ср.', em_tag, base_script=SCRIPT_CIVIL)
        text += '%s%s' % (s, NBSP)
    elif ref == 'qv':
        s = Segment('см.', em_tag, base_script=SCRIPT_CIVIL)
        text += '%s%s' % (s, NBSP)
    elif ref == 'ref':
        pass

    DEFAULT_SEP = ','
    if seps:
        seps = seps[1:-1].split('}{')
        if not seps[0]:
            seps[0] = DEFAULT_SEP
        _s = Segment(seps[0], text_tag, base_script=SCRIPT_CIVIL)
        tmp = str(_s)
        if re.match(r'\w', seps[0][0:]):
            tmp = SPACE + tmp
        if re.match(r'\w', seps[0][-1:]) or seps[0][-1:] in ',;':
            tmp += SPACE
        last_sep = sep = tmp
        if len(seps) > 1:
            _s = Segment(seps[1], text_tag, base_script=SCRIPT_CIVIL)
            tmp = str(_s)
            if re.match(r'\w', seps[1][0:]):
                tmp = SPACE + tmp
            if re.match(r'\w', seps[1][-1:]) or seps[1][-1:] in ',;':
                tmp += SPACE
            last_sep = tmp
    else:
        _s = Segment(DEFAULT_SEP, text_tag, base_script=SCRIPT_CIVIL)
        tmp = str(_s)
        if re.match(r'\w', DEFAULT_SEP[0:]):
            tmp = SPACE + tmp
        if re.match(r'\w', DEFAULT_SEP[-1:]) or DEFAULT_SEP[-1:] in ',;':
            tmp += SPACE
        last_sep = sep = tmp

    ents = [re.findall(RE_PARSE_REF_ENTRY, ent)[0]
            for ent in ents[1:-1].split('][')]

    for j, (word, num, meanings) in enumerate(ents):
        if j > 0:
            if len(ents) == j + 1:
                text += last_sep
            else:
                text += sep
        params = {
            'civil_equivalent': word,
        }
        if num:
            params['homonym_order'] = int(num)

        from slavdict.dictionary.models import Entry
        entry = Entry.objects.get(**params)

        headword = hyphenate_ucs8(entry.base_vars[0].idem_ucs)
        s = Segment(headword, csl_tag, base_script=SCRIPT_CSLAV)
        if for_web:
            if ref_func:
                url = ref_func(entry)
            else:
                url = entry.get_absolute_url()
            text += '<a href="%s">%s</a>' % (url, s)
        else:
            text += str(s)

        if num:
            s = Segment(num, number_tag, base_script=SCRIPT_CIVIL)
            text += str(s)

        if meanings:
            s = Segment('в знач.', text_tag, base_script=SCRIPT_CIVIL)
            text += SPACE + str(s) + NBSP
            meanings = [Segment(i, text_tag, base_script=SCRIPT_CIVIL)
                        for i in re.split(r'[\s,]+', meanings)]
            for i, s in enumerate(meanings):
                if i == 0:
                    text += str(s)
                elif i == len(meanings) - 1:
                    conj = Segment('и', text_tag, base_script=SCRIPT_CIVIL)
                    text += SPACE + str(conj) + NBSP + str(s)
                else:
                    comma = Segment(',', text_tag, base_script=SCRIPT_CIVIL)
                    text += str(comma) + SPACE + str(s)

    if ref == 'idem':
        segs = (
            NBSP,
            Segment('(', text_tag, base_script=SCRIPT_CIVIL),
            Segment('см.', em_tag, base_script=SCRIPT_CIVIL),
            Segment(')', text_tag, base_script=SCRIPT_CIVIL),
        )
        text += ''.join(str(s) for s in segs)

    if '\u00a0' in s1:
        text = NBSP + text
    elif ' ' in s1:
        text = SPACE + text
    if '\u00a0' in s2:
        text += NBSP
    elif ' ' in s2:
        text += SPACE

    return text

@register_filter
def ind_refs(value, for_web=False, ref_func=None):
    """ Подставновка шаблонов ссылок:

      idem[врачь]   --> то же, что врачь (см.)
      cf[восприяти] --> ср. восприяти
      qv[ныне]      --> см. ныне
      ref[весь]     --> весь

      idem[брак1-2]   --> то же, что брак¹, в знач. 2 (см.)
      cf[бежати-2,3]  --> ср. бежати, в знач. 2, 3

      qv[водотрудие][воднотрудование] --> см. водотрудие, воднотрудование
      cf[а1][б][в]{и}                 --> ср. а¹ и б и в
      cf[а1][б][в]{,}{и}              --> ср. а¹, б и в

      <лексема> ::= "[" <гражданское написание лексемы>
            [<номер омонима>] ["-" <список номеров значений>] "]"
      <разделитель> ::= "{" <текст разделителя без конечного пробела> "}"
      <шаблон ссылки> ::= < idem|cf|qv|ref > <лексема>{1,} <разделитель>{0,2}

      Если разделитель один, он используется во всех случаях. Если их два, то
      второй -- это разделитель для объединения двух последних элементов
      списка.

    """
    text = ''
    for i, x in enumerate(re.split('(%s)' % RE_FIND_REF, value)):
        if i % 2 == 1:
            try:
                text += insert_ref(x, for_web=for_web, ref_func=ref_func)
            except MultipleObjectsReturned:
                text += x + ('[ ###### Ошибка! Ссылка задана недостаточно '
                    'специфично -- по гражданскому написанию найдено '
                    'несколько статей вместо одной ] ')
            except ObjectDoesNotExist:
                text += x + '[ ###### Ошибка! Статья по ссылке не найдена ] '
            except Exception as e:
                text += x + '[ ###### При обработке ссылки возникла ' + \
                            'ошибка: %s ] ' % e
        elif x:
            text += x
    return text

@register_filter
def web_refs(value, ref_func=None):
    return ind_refs(value, for_web=True, ref_func=ref_func)

@register_filter
def ind_collocation_special_cases(words, for_web=False):
    """ Особая обработка словосочетаний
    """
    # 1) Все случаи ", -" давать гражданкой
    for segments in words.in_betweens:
        n = len(segments)
        if n < 3:
            continue
        for i in range(n):
            comma = segments[i].type == Segment.TYPE_COMMA
            two_more_last_symbols = i + 3 == n
            last_hyphen =  segments[-1].type == Segment.TYPE_HYPHEN
            if comma and two_more_last_symbols and last_hyphen:
                segments[i].output_script = SCRIPT_CIVIL
                segments[-1].output_script = SCRIPT_CIVIL

    # 2) Запятую в последовательности "ѻтє'цъ, ѻц~є'въ" дать гражданкой
    for i, word in enumerate(words.words):
        first_match = word.segment == 'nтє1цъ'
        one_more_word = i + 1 < len(words.words)
        second_match = one_more_word and words.words[i + 1].segment == 'nц7є1въ'
        in_between = words.in_betweens[i + 1]
        comma = in_between and in_between[0].type == Segment.TYPE_COMMA
        if first_match and second_match and comma:
            in_between[0].output_script = SCRIPT_CIVIL

    return words

@register_filter
def web_collocation_special_cases(words):
    return ind_collocation_special_cases(words, for_web=True)

@register_filter
def ind_csl_special_cases(words, for_web=False):
    """ Особая обработка цсл текста при значении
    """
    # 1) Все ";" давать гражданкой
    for segments in words.in_betweens:
        n = len(segments)
        if n < 2:
            continue
        for i in range(n):
            if segments[i].type == Segment.TYPE_SEMICOLON:
                segments[i].output_script = SCRIPT_CIVIL

    return words

@register_filter
def web_csl_special_cases(words):
    return ind_csl_special_cases(words, for_web=True)

@register_filter
def has_no_accent(value):
    r = re.compile(r"['`\^~А-Щ]")
    if re.findall(r, value):
        return False
    return True

register_filter('old_cslav_words')(cslav_nobr_words)
register_filter('ind_cslav_words')(cslav_words)

@register_filter
def web_cslav_words(value, cstyle=CSL_CSTYLE, civil_cstyle=None):
    return cslav_words(value, cstyle, civil_cstyle, for_web=True)
