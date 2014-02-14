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

{% space %} -- Непарный вспомогательный тэг для использования внутри {% trim %}.
Гарантирует наличие единичного пробела, если только не будет перекрыт тэгом {% backspace %}.

{% backspace %} -- Непарный вспомогательный тэг для использования внутри {% trim %},
когда нужно перекрыть {% space %}. Удаляет перед собой любые пробельные пространства
до ближайшего текста или тэга. Пробельное пространство может в частности содержать
символьные ссылки &nbsp;

{% punct %} -- Непарный вспомогательный тэг для использования внутри {% trim %}.
В том случае если текст внутри тэга кончается на знак препинания, гарантирует
наличие за ним пробела. К сожалению, пока его использоание регулируется слишком
жесткими правилами. Его необходимо помещать между тэгами, в которых будет текст.
Помещать внутрь таких тегов его нельзя. Впоследствии его надо будет каким-то
образом переделать.

"""
import re

from django.utils.functional import allow_lazy
from django.utils.encoding import force_unicode

from jinja2 import nodes
from jinja2.ext import Extension

from coffin import template
register = template.Library()

def strip_spaces_between_tags_and_text(value):
    value = re.sub(ur'>\s+', u'>', force_unicode(value.strip()))
    value = re.sub(ur'\s+<', u'<', value)
    # {{ space }}
    value = re.sub(u'\u0007', u' ', value)
    # {{ backspace }}
    #  Звёздочка вместо плюса нужна, чтобы \u0008 (backspace) были удалены
    #  в любом случае независимо от того, предшествует им пробел или нет.
    value = re.sub(ur'((\s)|(&nbsp;))*\u0008', u'', value)
    # {{ punct }}
    value = re.sub(ur'\u1900(<[^>]+>)([\.,:;\!\?])', ur'\1\2', value)
    value = re.sub(ur'\u1900', u' ', value)
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
        # {{ space }}
        source = re.sub(ur'{{\s*space\s*}}', ur'\u0007', source)
        # {{ backspace }}
        source = re.sub(ur'{{\s*backspace\s*}}', ur'\u0008', source)
        # {{ punct }}
        source = re.sub(ur'{{\s*punct\s*}}', ur'\u1900', source)
        return source

trim = TrimExtension

@register.filter
def cslav_words(value):
    value = value.replace(u'...', u'<span>...</span>')
    pattern = u'<span class="cslav nobr">%s</span>'
    words = (pattern % word for word in value.split())
    return u'&#32;'.join(words)
