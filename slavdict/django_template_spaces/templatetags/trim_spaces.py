# -*- coding: utf-8 -*-
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

{{ nbsp }} -- неразрывный пробел, no-break space, U+00A0.

{{ nbhyphen }} -- non-breaking hyphen, U+2011.

{{ softhyphen }} -- soft hyphen, U+00AD.

{{ wj }}, {{ zwnbsp }} -- word joiner WJ = zero width no-break space ZWNBSP,
U+2060. В стандарте Юникод ZWNBSP это U+FEFF, который также используется как
BOM. Начиная с версии 3.2 использование позиции U+FEFF как ZWNBSP объявлено
устаревшим и в этой ф-ции надо использовать WJ (U+2060).

{{ newline }} -- конец абзаца и начало нового.

"""
import re

from django.utils.functional import allow_lazy
from django.utils.encoding import force_unicode

from jinja2 import nodes
from jinja2.ext import Extension
from coffin import template

from slavdict.dictionary.models import ucs_convert, html_escape, html_unescape

register = template.Library()
BACKSPACE = u'\u0008'
EXCLAM = u'\u1991'
NBSP = u'\uEEA0'
NEWLINE = u'\uEEEE'
ONLYDOT = u'\u1902'
PUNCT = u'\u1900'
SPACE = u'\u0007'
SPACES = SPACE + NBSP + NEWLINE

def strip_spaces_between_tags_and_text(value):
    value = re.sub(ur'>\s+', u'>', force_unicode(value.strip()))
    value = re.sub(ur'\s+<', u'<', value)
    # {{ backspace }}
    # Звёздочка вместо плюса нужна, чтобы backspace'ы были удалены
    # в любом случае независимо от того, предшествует им пробел или нет.
    value = re.sub(ur'([\s{spaces}]|&nbsp;)*{backspace}'.format(
                           spaces=SPACES, backspace=BACKSPACE), u'', value)
    # {{ punct }}
    value = re.sub(PUNCT + ur'(<[^>]+>)([\.,:;\!\?])', ur'\1\2', value)
    value = re.sub(PUNCT, u' ', value)
    # {{ ! }}
    value = re.sub(EXCLAM, u'', value)
    # {{ onlyDot }}
    value = re.sub(ur'([\.…])((\s)|(&nbsp;))*' + ONLYDOT, ur'\1', value)
    value = re.sub(ur'((\s)|(&nbsp;))*' + ONLYDOT, ur'.', value)
    # {{ newline }}
    value = re.sub(NEWLINE, u'\n', value)
    # {{ nbsp }}
    value = re.sub(NBSP, u'\u00A0', value)
    # {{ space }}
    value = re.sub(SPACE, u' ', value)
    return value
strip_spaces_between_tags_and_text = allow_lazy(strip_spaces_between_tags_and_text, unicode)

class TrimExtension(Extension):

    tags = set(['trim'])

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endtrim'], drop_needle=True)
        return nodes.CallBlock(
            self.call_method('_strip_spaces', [], [], None, None),
            [], [], body,
        ).set_lineno(lineno)

    def _strip_spaces(self, caller=None):
        return strip_spaces_between_tags_and_text(caller().strip())

    def preprocess(self, source, name, filename=None):
        source = re.sub(ur'{{\s*space\s*}}', SPACE, source)
        source = re.sub(ur'{{\s*backspace\s*}}', BACKSPACE, source)
        source = re.sub(ur'{{\s*punct\s*}}', PUNCT, source)
        source = re.sub(ur'{{\s*!\s*}}', EXCLAM, source)
        source = re.sub(ur'{{\s*onlyDot\s*}}', ONLYDOT, source)
        source = re.sub(ur'{{\s*nbsp\s*}}', NBSP, source)
        source = re.sub(ur'{{\s*newline\s*}}', NEWLINE, source)

        # {{ nbhyphen }}
        source = re.sub(ur'{{\s*nbhyphen\s*}}', ur'\u2011', source)
        # {{ softhyphen }}
        source = re.sub(ur'{{\s*softhyphen\s*}}', ur'\u00AD', source)
        # {{ wj }}, {{ zwnbsp }}
        source = re.sub(ur'{{\s*wj\s*}}', ur'\u2060', source)
        source = re.sub(ur'{{\s*zwnbsp\s*}}', ur'\u2060', source)
        # {{ emspace }}, {{ enspace }}
        source = re.sub(ur'{{\s*emspace\*}}', u'\u2003', source)
        source = re.sub(ur'{{\s*enspace\*}}', u'\u2002', source)
        return source

trim = TrimExtension

def cslav_nobr_words(value):
    """ Все слова в переданном тексте делает неразрывными, чтобы браузер их
    случайно не порвал посередине. Все многоточия, скобки и косые черты
    помечает для отображения гражданской графикой, а остальное --
    церковнославянской.

    """
    # многоточие, круглые, квадратные скобки и косая черта
    value = re.sub(ur'(\.\.\.|[\(\)\[\]/])', ur'<span>\1</span>', value)
    pattern = u'<span class="cslav nobr">%s</span>'
    words = (pattern % word for word in value.split())
    return u'&#32;'.join(words)

def make_soft_hyphens(segment):
    text = segment[:2]
    for c in segment[2:-2]:
        if c not in u'!#$%&+,-.12345678:;<=>?@C\\^_bcdg~·':
            text += u'\u00AD' + c
        else:
            text += c
    if len(segment) > 3:
        text += segment[-2:]
    elif len(segment) == 3:
        text += segment[-1:]
    return text

def indesign_cslav_words(value, *args):
    """ Аналог cslav_nobr_words для импорта в InDesign. """
    if value is None:
        value = u''
    cstyle = u'CSLSegment'
    if args:
        cstyle = args[0]
    TEXT_TAG = u'%s'
    CSL_TAG = u'<w aid:cstyle="{}">%s</w>'.format(cstyle)
    # многоточие
    RE_DOTS = ur'\.\.\.'
    # круглые, квадратные скобки и косая черта
    RE_BRACES_SLASH = ur'[\(\)\[\]/]'
    RE = re.compile(u'(%s|%s)' % (RE_DOTS, RE_BRACES_SLASH))

    segments = []
    for segment in value.split():
        parts = []
        m = RE.search(segment)
        while m:
            start, end = m.start(), m.end()
            left = segment[:start]
            center = segment[start:end]
            right = segment[end:]

            if left:
                parts.append(CSL_TAG % html_escape(make_soft_hyphens(left)))

            center = re.sub(RE_BRACES_SLASH, TEXT_TAG % u'\g<0>', center)
            # NOTE: Замена точек должна происходить после замены скобок
            # и слэшей, поскольку сам TEXT_TAG содержит слэш.
            center = re.sub(RE_DOTS, TEXT_TAG % u'…', center)
            parts.append(center)

            segment = right
            m = RE.search(segment)
        if segment:
            parts.append(CSL_TAG % html_escape(make_soft_hyphens(segment)))
        segments.append(u''.join(parts))
    return SPACE.join(segments)


def cslav_subst(x):
    return EXCLAM + cslav_nobr_words(ucs_convert(x.group(1))) + EXCLAM

@register.filter
def cslav_injection(value):
    """ Заменяет текст вида ``## <text::antconc> ##`` на ``<text::ucs8>``.
    """
    value = re.sub(ur'##(.*?)##', cslav_subst, value)
    return value

def subst_func(func):
    def f(match):
        x, y, z = match.group(1), match.group(2), match.group(3)
        if u'\u00a0' in x:
            x = NBSP
        elif u' ' in x:
            x = SPACE
        if u'\u00a0' in z:
            z = NBSP
        elif u' ' in z:
            z = SPACE
        return u'%s%s%s' % (x, func(y), z)
    return f

ind_cslav = subst_func(lambda x: indesign_cslav_words(ucs_convert(x)))

@register.filter
def ind_cslav_injection(value):
    """ Заменяет текст вида ``## <text::antconc> ##`` на ``<text::ucs8>``.
    """
    return re.sub(ur'(\s*)##(.*?)##(\s*)', ind_cslav, value)

class MMM(object):
    def __init__(self, text):
        L = len(text)
        if L == len(text.strip()):
            self.match_groups = [None, u'', text, u'']
        else:
            LL = len(text.lstrip())
            LR = len(text.rstrip())
            x = u''
            if L > LL:
                x = text[:L - LL]
            y = text[L - LL:LR]
            z = u''
            if L > LR:
                z = text[LR:]
            self.match_groups = [None, x, y, z]
    def group(self, x):
        return self.match_groups[x]

@register.filter
def ind_civil_injection(value, cstyle):
    lst = value.split(u'##')
    TAG = u'<x aid:cstyle="{}">%s</x>'.format(cstyle)
    ind_civil = subst_func(lambda x: TAG % x)
    for i, elem in enumerate(lst):
        if not elem:
            continue
        if i % 2:
            elem = ind_civil(MMM(elem))
        else:
            elem = ind_cslav(MMM(elem))
        lst[i] = elem
    return u''.join(lst)

@register.filter
def ind_regex(value, cstyle, regex):
    """ Помечает указанным стилем cstyle найденный текст
    """
    TAG = u'<x aid:cstyle="{}">%s</x>'.format(cstyle)
    _ind_regex = subst_func(lambda x: TAG % x)
    return re.sub(ur'(\s*)(%s)(\s*)' % regex, _ind_regex, value)

@register.filter
def has_no_accent(value):
    r = re.compile(ur"['`\^~А-Щ]")
    if re.findall(r, value):
        return False
    return True

register.filter(name='cslav_words')(cslav_nobr_words)
register.filter(name='ind_cslav_words')(indesign_cslav_words)
