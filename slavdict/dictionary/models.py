# -*- coding: UTF-8 -*-
import datetime
import itertools
import json
import re

from collections import Counter, defaultdict

from django.db import models
from django.db import transaction
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import PositiveSmallIntegerField
from django.db.models import SmallIntegerField
from django.db.models import TextField
from django.db.utils import OperationalError
from django.db.utils import ProgrammingError
from django.utils.safestring import mark_safe

from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import antconc_ucs8
from hip2unicode.conversions import antconc_ucs8_without_aspiration
from hip2unicode.conversions import antconc_civilrus
from hip2unicode.conversions import antconc_antconc_wo_titles

from slavdict.custom_user.models import CustomUser

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

def meanings(self):
    objs = self.meaning_set
    objs = objs.filter(metaphorical=False, parent_meaning__isnull=True)
    objs = objs.order_by('order', 'id')
    return objs

def metaph_meanings(self):
    objs = self.meaning_set
    objs = objs.filter(metaphorical=True, parent_meaning__isnull=True)
    objs = objs.order_by('order', 'id')
    return objs

def all_meanings(self):
    objs = self.meaning_set
    return objs.filter(parent_meaning__isnull=True).order_by('order', 'id')

def has_meanings(self):
    return self.meaning_set.exists()

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

def _double_check(item1, item2, m2m=(), kwargs=None, model=None):
    if 'object_map' not in kwargs:
        kwargs['object_map'] = defaultdict(defaultdict)
    for x in m2m:
        x1 = getattr(item1, x)
        x2 = getattr(item2, x)
        for y in x1.all():
            y, z = y.make_double(**kwargs)
            kwargs['object_map'][y.__class__.__name__][y.pk] = z.pk
            x2.add(z)
        for y in x2.all():
            for f in y.__class__._meta.get_fields():
                if f.many_to_one and not hasattr(f, 'field'):
                    z = getattr(y, f.attname)
                    if z in kwargs['object_map'][y.__class__.__name__]:
                        setattr(y, f.attname,
                                kwargs['object_map'][y.__class__.__name__][z])
                        y.save()
    for f in model._meta.get_fields():
        if f.many_to_many and not hasattr(f, 'field'):
            x1 = getattr(item1, f.attname)
            x2 = getattr(item2, f.attname)
            for y in x1.all():
                x2.add(y)
    return item1, item2

NBSP = u'\u00A0'  # неразрывный пробел

BLANK_CHOICE = (('',''),)

PART_OF_SPEECH_CHOICES = (
    ('a', u'сущ.'),
    ('b', u'прил.'),
    ('c', u'мест.'),
    ('d', u'гл.'),
    ('e', u'[прич.]'),
    ('f', u'нареч.'),
    ('g', u'союз'),
    ('h', u'предл.'),
    ('i', u'част.'),
    ('j', u'межд.'),
    ('k', u'[число]'),
    ('l', u'[буква]'),
    ('m', u'прич.-прил.'),
    ('n', u'предик. нареч.'),
)
PART_OF_SPEECH_MAP = {
    'adjective': 'b',
    'adposition': 'h',
    'adverb': 'f',
    'conjunction': 'g',
    'interjection': 'j',
    'letter': 'l',
    'noun': 'a',
    'number': 'k',
    'participle-adjective': 'm',
    'participle': 'e',
    'particle': 'i',
    'postposition': 'h',
    'predicative adverb': 'n',
    'preposition': 'h',
    'pronoun': 'c',
    'verb': 'd',
}

TANTUM_CHOICES = (
    ('d', u'только дв.'),
    ('p', u'только мн.'),
)
TANTUM_MAP = {
    'dualeTantum': 'd',
    'pluraleTantum': 'p',
}

GENDER_CHOICES = (
    ('m', u'м.'),
    ('f', u'ж.'),
    ('n', u'с.'),
    ('d', u'м. и' + NBSP + u'ж.'),
)
GENDER_MAP = {
    'masculine': 'm',
    'feminine': 'f',
    'neutral': 'n',
    'dual': 'd',
}

ONYM_CHOICES = (
    ('', u'не имя собст.'),
    ('a', u'имя'),
    ('b', u'топоним'),
    ('c', u'народ/общность людей'),
    ('d', u'[другое]'),
)
ONYM_MAP = {
    'anthroponym': 'a',
    'toponym': 'b',
    'ethnonym': 'c',
    'other': 'd',
}

TRANSITIVITY_CHOICES = (
    ('', u''),
    ('t', u'перех.'),
    ('i', u'неперех.'),
    ('b', u'перех. и неперех.'),
)
TRANSITIVITY_MAP = {
    'transitive': 't',
    'intransitive': 'i',
    'labile': 'b',
}

# TODO: Должен остаться только один
# из этих двух списков для причастий.
PARTICIPLE_TYPE_CHOICES = (
    ('a', u'действ. прич. наст. вр.'),
    ('b', u'действ. прич. прош. вр.'),
    ('c', u'страд. прич. наст. вр.'),
    ('d', u'страд. прич. прош. вр.'),
)
PARTICIPLE_CHOICES = (
    ('1', u'действ. наст.'),
    ('2', u'действ. прош.'),
    ('3', u'страд. наст.'),
    ('4', u'страд. прош.'),
)
PARTICIPLE_TYPE_MAP = {
    'pres_act': 'a',
    'perf_act': 'b',
    'pres_pass': 'c',
    'perf_pass': 'd',
}

STATUS_CHOICES = (
    ('c', u'создана'),
    ('w', u'в работе'),
    ('g', u'поиск греч.'),
    ('f', u'завершена'),
    ('e', u'редактируется'),
    ('a', u'утверждена'),
)
STATUS_MAP = {
    'approved': 'a',
    'beingEdited': 'e',
    'created': 'c',
    'finished': 'f',
    'greek': 'g',
    'inWork': 'w',
}

LANGUAGE_CHOICES = (
    ('a', u'греч.'),
    ('b', u'ивр.'),
    ('c', u'аккад.'),
    ('d', u'арам.'),
    ('e', u'арм.'),
    ('f', u'груз.'),
    ('g', u'копт.'),
    ('h', u'лат.'),
    ('i', u'сир.'),
)
LANGUAGE_MAP = {
    'akkadian': 'c',
    'aramaic': 'd',
    'armenian': 'e',
    'coptic': 'g',
    'georgian': 'f',
    'greek': 'a',
    'hebrew': 'b',
    'latin': 'h',
    'syriac': 'i',
}
ETYMOLOGY_LANGUAGE_INDESIGN_CSTYLE = {
    LANGUAGE_MAP['greek']: 'Greek',
    LANGUAGE_MAP['latin']: 'Latin',
}
ETYMOLOGY_LANGUAGES = ETYMOLOGY_LANGUAGE_INDESIGN_CSTYLE.keys()
LANGUAGE_CSS = {
        LANGUAGE_MAP['akkadian']: 'akkadian',
        LANGUAGE_MAP['aramaic']: 'aramaic',
        LANGUAGE_MAP['armenian']: 'armenian',
        LANGUAGE_MAP['coptic']: 'coptic',
        LANGUAGE_MAP['georgian']: 'georgian',
        LANGUAGE_MAP['greek']: 'grec',
        LANGUAGE_MAP['hebrew']: 'hebrew',
        LANGUAGE_MAP['latin']: '',
        LANGUAGE_MAP['syriac']: 'syriac',
}
LANGUAGE_TRANSLIT_CSS = {
        LANGUAGE_MAP['akkadian']: '',
        LANGUAGE_MAP['aramaic']: 'aramaic-translit',
        LANGUAGE_MAP['armenian']: '',
        LANGUAGE_MAP['coptic']: '',
        LANGUAGE_MAP['georgian']: '',
        LANGUAGE_MAP['greek']: '',
        LANGUAGE_MAP['hebrew']: 'hebrew-translit',
        LANGUAGE_MAP['latin']: '',
        LANGUAGE_MAP['syriac']: 'syriac-translit',
}

SUBSTANTIVUS_TYPE_CHOICES = (
    ('', ''),
    ('a', u'с.' + NBSP + u'ед.'),
    ('b', u'с.' + NBSP + u'мн.'),
    ('c', u'м.' + NBSP + u'ед.'),
    ('d', u'м.' + NBSP + u'мн.'),
    ('e', u'ж.' + NBSP + u'ед.'),
    ('f', u'ж.' + NBSP + u'мн.'),
)
SUBSTANTIVUS_TYPE_MAP = {
    'n.sg.': 'a',
    'n.pl.': 'b',
    'm.sg.': 'c',
    'm.pl.': 'd',
    'f.sg.': 'e',
    'f.pl.': 'f',
}

SC1, SC2, SC3, SC4, SC5, SC6, SC7, SC8, SC9, SC10 = 'abcdefghij'
ENTRY_SPECIAL_CASES = SC1, SC2, SC3, SC4, SC5, SC6, SC7, SC8, SC9, SC10
ENTRY_SPECIAL_CASES_CHOICES = (
    ('', ''),
    (SC1, u'Несколько лексем одного рода'),
    (SC2, u'2 лексемы, муж. и жен. рода'),
    (SC10, u'2 лексемы, муж. и ср. рода'),
    (SC3, u'2 лексемы, ср. и жен. рода'),
    (SC7, u'2 лексемы, жен. и ср. рода'),
    (SC4, u'2 лексемы, жен. и только мн.'),
    (SC5, u'2 лексемы, только мн. и жен.'),
    (SC6, u'3 лексемы, 3 муж. и последний неизм.'),
    (SC8, u'4 лексемы [вихрь]'),
    (SC9, u'Вынудить отображение пометы «неперех. и перех.» '
          u'при равном кол-ве перех. и неперех. значений'),
)
MSC1, MSC2, MSC3, MSC4, MSC5, MSC6, MSC7, MSC8, MSC9, MSC10 = 'abcdefghij'
MSC11, MSC12, MSC13, MSC14, MSC15, MSC16, MSC17 = 'klmnopq'
MEANING_SPECIAL_CASES_CHOICES = (
    ('', ''),
    (u'Имена', (
        (MSC1,  u'канонич.'),
        (MSC8,  u'имя собств.'),
        (MSC9,  u'топоним'),
    )),
    (u'Части речи', (
        (MSC6,  u'нареч.'),
        (MSC13, u'союз'),
        (MSC2,  u'предл.'),
        (MSC3,  u'част.'),
        (MSC7,  u'межд.'),
    )),
    (u'Формы слова', (
        (MSC4,  u'дат.'),
        (MSC11, u'мн.'),
        (MSC5,  u'твор. ед. в роли нареч.'),
        (MSC12, u'в роли нареч.'),
        (MSC14, u'в роли прил.'),
        (MSC15, u'в роли част.'),
    )),
    (u'Другое', (
        (MSC10, u'преимущ.'),
        (MSC16, u'полувспом.'),  # Полувспомогательный глагол
        (MSC17, u'безл.'),  # Безличное употребление глагола
    )),
)
POS_SPECIAL_CASES = (MSC2, MSC3, MSC6, MSC7, MSC13)
POS_SPECIAL_CASES_MAP = {
    MSC2: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['preposition']],
    MSC3: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['particle']],
    MSC6: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['adverb']],
    MSC7: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['interjection']],
    MSC13: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['conjunction']],
}

YET_NOT_IN_VOLUMES = None
VOLUME_LETTERS = {
    1: (u'а', u'б'),
    2: (u'в',),
}
ANY_LETTER = None

class WithoutHiddenManager(models.Manager):
    def get_queryset(self):
        return super(WithoutHiddenManager,
                     self).get_queryset().filter(hidden=False)

class JSONSerializable(object):

    def forJSON(self):
        raise NotImplementedError

    def toJSON(self):
        return json.dumps(self.forJSON(),
                          ensure_ascii=False, separators=(',',':'))


class Entry(models.Model, JSONSerializable):

    civil_equivalent = CharField(u'гражд. написание', max_length=50)
    civil_inverse = CharField(u'гражд. инв.', max_length=50)

    @property
    def orth_vars(self):
        return self.orthographic_variants.all()

    @property
    def orth_vars_refs(self):
        return self.orthographic_variants.filter(no_ref_entry=False)

    @property
    def base_vars(self):
        return self.orthographic_variants.filter(parent__isnull=True)

    hidden = BooleanField(u'Скрыть лексему', help_text=u'''Не отображать лексему
            в списке словарных статей.''', default=False, editable=False)

    homonym_order = SmallIntegerField(u'номер омонима', help_text=u'''Арабская
            цифра, например, 1, 2, 3... Поле заполняется только при наличии
            нескольких омонимов.''', blank=True, null=True)

    homonym_gloss = CharField(u'подсказка', max_length=40, help_text=u'''
            Пояснение для различения омонимов, например: «предварять» для
            ВАРИТИ I или «варить» для ВАРИТИ II. Предполагается использовать
            только для служебных целей, а не для отображения при словарных
            статьях.''', blank=True)

    duplicate = BooleanField(u'дубликат', help_text=u'''В нормальном случае
            дубликатов словарных статей быть не должно. Они возникают только
            в результате недосмотра при создании новый статей вручную или в
            результате недостаточно хороших проверок при автоматизированном
            импорте заготовок статей.''', default=False)

    part_of_speech = CharField(u'часть речи', max_length=1,
            choices=BLANK_CHOICE + PART_OF_SPEECH_CHOICES, default='',
            blank=True)

    def is_part_of_speech(self, *slugs):
        for slug in slugs:
            if PART_OF_SPEECH_MAP[slug] == self.part_of_speech:
                return True

    # Для сущ. и прил.
    uninflected = BooleanField(u'неизменяемое', default=False)

    word_forms_list = TextField(u'список словоформ', help_text=u'''Список
            словоформ через запятую''', blank=True)

    # только для существительных
    tantum = CharField(u'число', choices=TANTUM_CHOICES,
                       max_length=1, blank=True, default='')

    def is_tantum(self, slug):
        return TANTUM_MAP[slug] == self.tantum

    gender = CharField(u'род', choices=GENDER_CHOICES,
                       max_length=1, blank=True, default='')

    def is_gender(self, slug):
        return GENDER_MAP[slug] == self.gender

    genitive = CharField(u'форма Р. падежа', max_length=50, blank=True)

    @property
    def genitive_ucs_wax(self):
        return ucs_affix_or_word(self.genitive)

    @property
    def genitives(self):
        RE_COMMA = ur'[,\s]+'
        words = re.split(RE_COMMA, self.genitive)
        return [(word, ucs_convert(word)) for word in words]

    onym = CharField(u'тип имени собственного', max_length=1, blank=True,
                     choices=ONYM_CHOICES, default='')

    def is_onym(self, slug):
        return ONYM_MAP[slug] == self.onym

    canonical_name = BooleanField(u'каноническое', default=False)

    nom_sg = CharField(u'И.мн.', help_text=u'''Только для этнонимов
                       (например, в словарной статье АГАРЯНИН, здесь --
                       АГАРЯНЕ).''', max_length=50, blank=True, default='')
    @property
    def nom_sg_ucs_wax(self):
        return ucs_affix_or_word(self.nom_sg)

    @property
    def ethnonyms(self):
        RE_COMMA = ur'[,\s]+'
        words = re.split(RE_COMMA, self.nom_sg)
        return [(word, ucs_convert(word)) for word in words]

    # только для прилагательных
    short_form = CharField(u'краткая форма', help_text=u'''Если Вы указываете
                           не всё слово, а только его часть, предваряйте её
                           дефисом.''', max_length=50, blank=True)

    @property
    def short_form_ucs_wax(self):
        return ucs_affix_or_word(self.short_form)

    @property
    def short_forms(self):
        RE_COMMA = ur'[,\s]+'
        words = re.split(RE_COMMA, self.short_form)
        return [(word, ucs_convert(word)) for word in words]

    possessive = BooleanField(u'притяжательное', default=False,
                              help_text=u'Притяжательное прилагательное.')

    # только для глаголов
    transitivity = CharField(u'переходность', max_length=1, blank=True,
                             choices=TRANSITIVITY_CHOICES, default='')

    def is_transitivity(self, slug):
        return TRANSITIVITY_MAP[slug] == self.transitivity

    @property
    def transitivity_from_meanings(self):
        labile = TRANSITIVITY_MAP['labile']
        trans = TRANSITIVITY_MAP['transitive']
        intrans = TRANSITIVITY_MAP['intransitive']
        tmap = dict(TRANSITIVITY_CHOICES)
        lst = filter(None, (m.transitivity for m in self.meanings))
        template = u'%s и\u00a0%s'
        if len(lst) == 0:
            return u''
        elif len(set(lst)) == 1 and \
                not (lst[0] == labile and self.special_case == SC9):
            return tmap.get(lst[0], u'')
        else:
            c = Counter(lst)
            if labile in c:
                c[trans] += c[labile]
                c[intrans] += c[labile]
            if c[trans] < c[intrans] or \
                    c[trans] >= c[intrans] and self.special_case == SC9:
                return template % (tmap[intrans], tmap[trans])
            else:
                return template % (tmap[trans], tmap[intrans])

    sg1 = CharField(u'форма 1 ед.', max_length=50, blank=True,
                    help_text=u'''Целая словоформа или окончание. В случае
                    окончания первым символом должен идти дефис.''')

    @property
    def sg1_ucs_wax(self):
        return ucs_affix_or_word(self.sg1)

    @property
    def several_sg1(self):
        RE_COMMA = ur'[,\s]+'
        words = re.split(RE_COMMA, self.sg1)
        return [(word, ucs_convert(word)) for word in words]

    sg2 = CharField(u'форма 2 ед.', max_length=50, blank=True,
                    help_text=u'''Целая словоформа или окончание. В случае
                    окончания первым символом должен идти дефис.''')

    @property
    def sg2_ucs_wax(self):
        return ucs_affix_or_word(self.sg2)

    participle_type = CharField(u'тип причастия', max_length=1, blank=True,
                                choices=PARTICIPLE_TYPE_CHOICES, default='')

    def is_participle_type(self, slug):
        return PARTICIPLE_TYPE_MAP[slug] == self.participle_type

    derivation_entry = ForeignKey('self', verbose_name=u'образовано от',
            related_name='derived_entry_set', blank=True, null=True)

    link_to_entry = ForeignKey('self', verbose_name=u'ссылка на другую лексему',
            help_text=u'''Если вместо значений словарная статья должна содержать
            только ссылку на другую словарную статью, укажите её в данном
            поле.''', related_name='ref_entry_set', blank=True, null=True)

    link_to_collogroup = ForeignKey('CollocationGroup',
            verbose_name=u'ссылка на словосочетание', help_text=u'''Если вместо
            значений словарная статья должна содержать только ссылку на
            словосочетание, укажите его в данном поле.''',
            related_name='ref_entry_set', blank=True, null=True)

    link_to_meaning = ForeignKey('Meaning', verbose_name=u'ссылка на значение',
            help_text=u'''Если вместо значений словарная статья должна
            содержать только ссылку на опредленное значение лексемы или
            словосочетания, укажите его в данном поле.''',
            related_name='ref_entry_set', blank=True, null=True)

    cf_entries = ManyToManyField('self', verbose_name=u'ср. (лексемы)',
            related_name='cf_entry_set', symmetrical=False, blank=True,
            null=True)

    cf_collogroups = ManyToManyField('CollocationGroup',
            verbose_name=u'ср. (группы слововосочетаний)',
            related_name='cf_entry_set', blank=True, null=True)

    cf_meanings = ManyToManyField('Meaning', verbose_name=u'ср. (значения)',
            related_name='cf_entry_set', blank=True, null=True)

    @property
    def cfmeanings(self):
        return self.cf_meanings.all()

    @property
    def cfentries(self):
        return self.cf_entries.all()

    @property
    def cfcollogroups(self):
        return self.cf_collogroups.all()

    additional_info = TextField(u'примечание к статье',
            help_text=u'''Любая дополнительная информация по данной ЛЕКСЕМЕ.
            Дополнительная информация по значению лексемы или примеру на
            значение указывается не здесь, а в аналогичных полях при значении
            и примере, соответственно.''', blank=True)

    @property
    def etymologies(self):
        etyms = self.etymology_set.filter(language__in=ETYMOLOGY_LANGUAGES)
        etyms = list(etyms)
        etyms.sort(key=lambda x:(bool(x.etymon_to), x.order, x.id))
        return etyms

    @property
    def collogroups(self):
        return self.collocationgroup_set.all().order_by('order', 'id')

    @property
    def participles(self):
        return self.participle_set.all().order_by('order', 'id')

    # административная информация
    status = CharField(u'статус статьи', max_length=1, choices=STATUS_CHOICES,
                       default='c')

    def is_status(self, slug):
        return STATUS_MAP[slug] == self.status

    percent_status = PositiveSmallIntegerField(
                        u'статус готовности статьи в процентах', default=0)

    authors = ManyToManyField(CustomUser, verbose_name=u'автор статьи',
                    blank=True, null=True)

    antconc_query = TextField(u'Запрос для программы AntConc', blank=True)
    mtime = DateTimeField(editable=False)
    ctime = DateTimeField(editable=False, auto_now_add=True)

    good = TextField(u'Годность статьи для показа', max_length=1, default=u'b',
                     choices=(
                         (u'b', u'не подходит'),  # bad
                         (u's', u'возможно, подходит'),  # so so
                         (u'g', u'подходит'),  # good
                     ))

    meanings = property(meanings)
    metaph_meanings = property(metaph_meanings)
    all_meanings = property(all_meanings)
    has_meanings = property(has_meanings)

    @property
    def meaning_groups(self):
        meaning_groups = []
        meanings = list(self.meanings)
        several_pos = False

        class MeaningGroup(object):
            def __init__(self, meanings, orthvars=tuple(), pos_mark=None):
                self.meanings = meanings
                self.orthvars = tuple(orthvars)
                self.pos_mark = pos_mark
                self.index_mark = None
                if len(meanings) > 1:
                    for i, meaning in enumerate(meanings):
                        meaning.index_mark = unicode(i + 1)
            def __len__(self):
                return len(self.meanings)
            def __iter__(self):
                return iter(self.meanings)
            def __getitem__(self, key):
                return self.meanings[key]

        class MeaningGroups(object):
            def __init__(self, meaning_groups, several_pos):
                self.meaning_groups = meaning_groups
                self.several_pos = several_pos
                if len(meaning_groups) > 1:
                    for i, mgroup in enumerate(meaning_groups):
                        mgroup.index_mark = {1: u'I', 2: u'II', 3: u'III',
                                             4: u'IV', 5: u'V'}[i + 1]
            def __len__(self):
                return len(self.meaning_groups)
            def __iter__(self):
                return iter(self.meaning_groups)
            def __getitem__(self, key):
                return self.meaning_groups[key]

        if any(o.use for o in self.orth_vars):
            d = defaultdict(list)
            dd = defaultdict(list)
            for o in self.orth_vars:
                if o.use:
                    for i in o.use.strip().split(','):
                        i = int(i)
                        d[i].append(o.idem_ucs)
            for i in d:
                dd[tuple(sorted(d[i]))].append(i)
            groups = [(key, sorted(value)) for key, value in dd.items()]
            if all(len(value) == 1 for key, value in groups):
                for orthvars_list, meaning_numbers in groups:
                    m = meanings[meaning_numbers[0] - 1]
                    m.orthvars = orthvars_list
                group = MeaningGroup(meanings)
                meaning_groups.append(group)
            else:
                for orthvars_list, meaning_numbers in groups:
                    filtered_meanings = [m for i, m in enumerate(meanings)
                                           if i + 1 in meaning_numbers]
                    group = MeaningGroup(filtered_meanings, orthvars=orthvars_list)
                    meaning_groups.append(group)
                meaning_groups.sort(key=lambda mg: (mg.meanings[0].order,
                                                    mg.meanings[0].id))

        elif any(m.special_case and m.special_case in POS_SPECIAL_CASES
                 for m in meanings):
            several_pos = True
            ENTRY_POS = self.get_part_of_speech_display()
            pos = meanings[0].special_case
            mm = []
            for m in meanings:
                if m.special_case != pos:
                    pos_mark = POS_SPECIAL_CASES_MAP.get(pos, ENTRY_POS)
                    group = MeaningGroup(mm, pos_mark=pos_mark)
                    meaning_groups.append(group)
                    pos = m.special_case
                    mm = []
                mm.append(m)
            pos_mark = POS_SPECIAL_CASES_MAP.get(pos, ENTRY_POS)
            group = MeaningGroup(mm, pos_mark=pos_mark)
            meaning_groups.append(group)
        else:
            meaning_groups = [MeaningGroup(meanings)]
        return MeaningGroups(meaning_groups, several_pos)

    special_case = CharField(u'Статья нуждается в специальной обработке',
                             max_length=1, choices=ENTRY_SPECIAL_CASES_CHOICES,
                             default=u'', blank=True)

    def special_cases(self, case):
        RE_COMMA = ur'[,\s]+'
        if case == 'several nouns':
            if (self.genitive and ',' in self.genitive and
                    len(self.base_vars) > 1 and
                    self.special_case and
                    self.special_case in ENTRY_SPECIAL_CASES):
                M_GENDER = dict(GENDER_CHOICES)[GENDER_MAP['masculine']]
                F_GENDER = dict(GENDER_CHOICES)[GENDER_MAP['feminine']]
                N_GENDER = dict(GENDER_CHOICES)[GENDER_MAP['neutral']]
                PL_TANTUM = dict(TANTUM_CHOICES)[TANTUM_MAP['pluraleTantum']]
                UNINFL = u'неизм.'
                HIDDEN_GRAM = u''
                HIDDEN_FORM = u''

                wordforms = re.split(RE_COMMA, self.genitive)
                sc = self.special_case
                if SC1 == sc:
                    grammatical_marks = [HIDDEN_GRAM] * (len(wordforms) - 1)
                    grammatical_marks += [self.get_gender_display()]
                elif SC2 == sc:
                    grammatical_marks = [M_GENDER, F_GENDER]
                elif SC3 == sc:
                    grammatical_marks = [N_GENDER, F_GENDER]
                elif SC4 == sc:
                    grammatical_marks = [F_GENDER, PL_TANTUM]
                elif SC5 == sc:
                    grammatical_marks = [PL_TANTUM, F_GENDER]
                elif SC6 == sc:
                    grammatical_marks = [
                        HIDDEN_GRAM,
                        M_GENDER,
                        u'%s %s' % (M_GENDER, UNINFL)]
                    wordforms += [HIDDEN_FORM]
                elif SC7 == sc:
                    grammatical_marks = [F_GENDER, N_GENDER]
                elif SC8 == sc:
                    grammatical_marks = [HIDDEN_GRAM] * 3
                    grammatical_marks += [self.get_gender_display()]
                    wordforms = [HIDDEN_FORM, wordforms[0], HIDDEN_FORM, wordforms[1]]
                elif SC10 == sc:
                    grammatical_marks = [M_GENDER, N_GENDER]

                value = [(wordform, ucs_convert(wordform), grammatical_marks[i])
                         for i, wordform in enumerate(wordforms)]
                return value
        elif case == 'be' and self.civil_equivalent == u'быти':
            return [ucs_convert(x) for x in (u"нѣ'смь", u"нѣ'си")]
        elif case == 'bigger' and self.civil_equivalent == u'больший':
            return ucs_convert(u"вели'кій")

    def examples_groups_for_hellinists(self):
        if hasattr(self, '_exgroups'):
            return self._exgroups

        class ExamplesGroup(object):
            def __init__(self, examples, mg, m, cg=None):
                self.examples = examples
                self.meaning_group = mg
                self.meaning = m
                self.collogroup = cg
            def __len__(self):
                return len(self.examples)
            def __iter__(self):
                return iter(self.examples)

        exgroups = []
        for mgroup in self.meaning_groups:
            for meaning in mgroup.meanings:
                examples = []
                if meaning.examples:
                    examples.extend(meaning.examples)
                for submeaning in meaning.child_meanings:
                    examples.extend(submeaning.examples)
                exgroups.append(ExamplesGroup(examples, mgroup, meaning))
                collogroups = \
                        meaning.collogroups_non_phraseological + \
                        meaning.collogroups_phraseological
                for cg in collogroups:
                    cg_meanings = tuple(cg.meanings)
                    cg_metaph_meanings = tuple(cg.metaph_meanings)
                    meanings = cg_meanings + cg_metaph_meanings
                    for meaning in meanings:
                        exgroup = ExamplesGroup(meaning.examples,
                                                mgroup, meaning, cg)
                        exgroups.append(exgroup)
        self._exgroups = exgroups
        return exgroups

    # Залочена статья для редактирования,
    # во время подготовки тома к печати или нет.
    @property
    def preplock(self):
        if self.volume(volume=YET_NOT_IN_VOLUMES):
            return False
        return True

    def volume(self, volume=YET_NOT_IN_VOLUMES):
        first_letter = self.civil_equivalent.lstrip(u' =')[:1].lower()

        # Если аргумент volume не передан, то выбираем только те статьи,
        # для которых том ещё не определен.
        if volume is YET_NOT_IN_VOLUMES:
            used_letters = itertools.chain(*VOLUME_LETTERS.values())
            match = first_letter not in used_letters
        else:
            if isinstance(volume, (list, tuple)):
                volumes = volume
                used_letters = []
                for volume in volumes:
                    used_letters.extend(VOLUME_LETTERS.get(volume, []))
            else:
                used_letters = VOLUME_LETTERS.get(volume, [])
            match = first_letter in used_letters
        return match

    def starts_with(self, starts_with=ANY_LETTER):
        # Если аргумент starts_with не передан, то выбираем все статьи
        if starts_with is ANY_LETTER:
            return True
        leading = self.civil_equivalent.lstrip(u' =')[:len(starts_with)]
        return leading.lower() == starts_with.lower()

    @models.permalink
    def get_absolute_url(self):
        return ('single_entry_url', [str(self.id)])

    def save(self, without_mtime=False, *args, **kwargs):
        orth_vars = self.orth_vars
        if orth_vars:
            self.civil_equivalent = civilrus_convert(orth_vars[0].idem.strip())
            self.civil_inverse = self.civil_equivalent[::-1]
        if not without_mtime:
            self.mtime = datetime.datetime.now()
        super(Entry, self).save(*args, **kwargs)

    def make_double(self):
        with transaction.atomic():
          id1 = self.pk
          e2 = self
          e2.pk = None
          e2.homonym_gloss = u''
          e2.save()
          e1 = Entry.objects.get(pk=id1)
          m2m = ('participle_set', 'orthographic_variants', 'etymology_set',
                 'collocationgroup_set', 'meaning_set')
                 # NOTE: example_set намеренно не добавляем, примеры имеет
                 # смысл обрабатывать только после того, как они будут
                 # добавлены к значениям.
          kwargs = {
              'entry': e2,
              'object_map': defaultdict(defaultdict),
          }
          e1, e2 = _double_check(e1, e2, m2m=m2m, kwargs=kwargs, model=Entry)

          # Очищаем kwargs от всех накопившихся ключей кроме исходных
          kwargs = {
              'entry': kwargs['entry'],
              'object_map': kwargs['object_map'],
          }
          # Дублируем только те примеры, которые относятся к статье в целом,
          # но не к словосочетанию и не к значению.
          for ex1 in e1.example_set.filter(meaning_id__isnull=True,
                                          collogroup_id__isnull=True):
              ex1, ex2 = ex1.make_double(**kwargs)
          return e1, e2
        return None, None

    def __unicode__(self):
        return self.orth_vars[0].idem

    def forJSON(self):
        _fields = (
            'additional_info',
            'antconc_query',
            'canonical_name',
            'civil_equivalent',
            'derivation_entry_id',
            'duplicate',
            'gender',
            'genitive',
            'good',
            'hidden',
            'homonym_gloss',
            'homonym_order',
            'id',
            'nom_sg',
            'onym',
            'part_of_speech',
            'participle_type',
            'possessive',
            'sg1',
            'sg2',
            'short_form',
            'status',
            'tantum',
            'uninflected',
        )
        dct = dict((key, self.__dict__[key]) for key in _fields)
        dct['participles'] = [p.forJSON() for p in self.participles]
        dct['orthvars'] = [ov.forJSON() for ov in self.orth_vars]
        dct['author_ids'] = [a[0] for a in self.authors.values_list('id')]
        dct['etymologies'] = [e.forJSON() for e in self.etymologies]
        dct['collogroups'] = [cg.forJSON() for cg in self.collogroups]
        dct['meanings'] = [m.forJSON() for m in self.all_meanings]
        dct['unsorted_examples'] = [e.forJSON()
                for e in self.example_set.filter(meaning__isnull=True)]
        return dct

    @property
    def host_entry(self):
        return self

    host = host_entry

    objects = WithoutHiddenManager()
    objects_all = models.Manager()

    class Meta:
        verbose_name = u'словарная статья'
        verbose_name_plural = u'СЛОВАРНЫЕ СТАТЬИ'
        ordering = ('-id',)

class Etymology(models.Model, JSONSerializable):

    entry = ForeignKey(Entry, verbose_name=u'словарная статья',
                help_text=u'''Словарная статья, к которой относится данная
                этимология.''', blank=True, null=True)

    collocation = ForeignKey('Collocation', verbose_name=u'словосочетание',
                help_text=u'''Словосочетание, к которому относится данная
                этимология.''', blank=True, null=True)

    order = SmallIntegerField(u'порядок следования', blank=True, default=345)

    etymon_to = ForeignKey('self', verbose_name=u'этимон для',
                help_text=u'''Возможный/несомненный этимон для другого этимона,
                который и необходимо указать.''', related_name='etymon_set',
                blank=True, null=True)

    @property
    def etymons(self):
        return self.etymon_set.filter(etymon_to=self.id).order_by('order', 'id')

    language = CharField(u'язык', max_length=1, choices=LANGUAGE_CHOICES,
                         default='')

    def is_language(self, x):
        if type(x) in (list, tuple):
            return self.language in [ix for ix in LANGUAGE_MAP if ix in x]
        else:
            return self.language == LANGUAGE_MAP[x]

    def has_etymology_language(self):
        return self.language in ETYMOLOGY_LANGUAGES

    def get_etymology_language_cstyle(self):
        return ETYMOLOGY_LANGUAGE_INDESIGN_CSTYLE.get(self.language, u'')

    def get_language_css(self):
        return LANGUAGE_CSS[self.language]

    def get_language_translit_css(self):
        return LANGUAGE_TRANSLIT_CSS[self.language]

    text = CharField(u'языковой эквивалент', max_length=40, blank=True)

    unitext = CharField(u'языковой эквивалент (Unicode)', max_length=40,
                        blank=True)

    translit = CharField(u'транслитерация', max_length=40, blank=True)
    meaning = CharField(u'перевод', max_length=70, blank=True)
    gloss = CharField(u'пояснение', max_length=70, blank=True)

    source = CharField(u'документальный источник',
                help_text=u'например, Септуагинта', max_length=40, blank=True)

    unclear = BooleanField(u'этимология неясна', default=False)
    questionable = BooleanField(u'этимология спорна', default=False)
    mark = CharField(u'грамматическая помета', max_length=20, blank=True)
    additional_info = TextField(u'примечание', blank=True)
    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        if self.entry:
            return self.entry
        else:
            try:
                host_entry = self.collocation.host_entry
            except:
                return None
            else:
                return host_entry

    @property
    def host(self):
        if self.entry:
            return self.entry
        else:
            return self.collocation

    def save(self, without_mtime=False, *args, **kwargs):
        super(Etymology, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Etymology, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
            id1 = self.pk
            et2 = self
            et2.pk = None
            if 'entry' in kwargs and 'collocation' not in kwargs:
                et2.entry = kwargs['entry']
            if 'collocation' in kwargs:
                et2.collocation = kwargs['entry']
            et2.save()
            et1 = Etymology.objects.get(pk=id1)
            return et1, et2
        return None, None

    def __unicode__(self):
        return u'%s %s %s' % (self.get_language_display(), self.entry,
                              self.translit)
    def forJSON(self):
        _fields = (
            'additional_info',
            'collocation_id',
            'entry_id',
            'etymon_to_id',
            'gloss',
            'id',
            'language',
            'mark',
            'meaning',
            'order',
            'questionable',
            'source',
            'text',
            'translit',
            'unclear',
            'unitext',
        )
        dct = dict((key, self.__dict__[key]) for key in _fields)
        dct['etimologies'] = [e.forJSON()
                for e in Etymology.objects.filter(etymon_to=self)]
        return dct

    class Meta:
        verbose_name = u'этимон'
        verbose_name_plural = u'этимология'
        ordering = ('id',)


class MeaningContext(models.Model, JSONSerializable):

    meaning = ForeignKey('Meaning', verbose_name=u'значение')
    order = SmallIntegerField(u'порядок следования', blank=True, default=345)

    left_text = CharField(u'дополнительный текст слева', max_length=50,
            help_text=u'''Здесь указывается текст на <span class="green"
            >русском</span> языке. Например, если необходим контекст «<span
            class="civil">+</span>&nbsp;<span class="cslav">къ</span
            >&nbsp;<span>class="civil">кому/чему</span>», в данное поле
            добавляется текст&nbsp;«<span class="typing">+</span>».''',
            blank=True)

    context = CharField(u'текст контекста', max_length=40,
            help_text=u'''Здесь указывается <span class="green"
            >церковнославянский</span> текст. Например, если необходим контекст
            «<span class="civil">+</span>&nbsp;<span class="cslav">къ</span
            >&nbsp;<span>class="civil">кому/чему</span>», в данное поле
            добавляется текст&nbsp;«<span class="typing">къ</span>».''',
            blank=True)

    @property
    def context_ucs(self):
        return ucs_convert(self.context)

    right_text = CharField(u'дополнительный текст справа', max_length=50,
            help_text=u'''Здесь указывается текст на <span class="green"
            >русском</span> языке. Например, если необходим контекст «<span
            class="civil">+</span>&nbsp;<span class="cslav">къ</span
            >&nbsp;<span>class="civil">кому/чему</span>», в данное поле
            добавляется текст&nbsp;«<span class="typing">кому/чему</span>».''',
            blank=True)

    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def show_in_dictionary(self):
        PL = u'мн.'
        L, C, R = self.left_text, self.context, self.right_text
        c1 = C and not L and not R
        c2 = not C and (L == PL or R == PL)
        if c1 or c2:
            return True
        return False

    @property
    def host_entry(self):
        try:
            host_entry = self.meaning.host_entry
        except:
            return None
        else:
            return host_entry

    @property
    def host(self):
        try:
            host = self.meaning.host
        except:
            return None
        else:
            return host

    def save(self, without_mtime=False, *args, **kwargs):
        super(MeaningContext, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(MeaningContext, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          mc2 = self
          mc2.pk = None
          if 'meaning' in kwargs:
              mc2.meaning = kwargs['meaning']
          mc2.save()
          mc1 = MeaningContext.objects.get(pk=id1)
          return mc1, mc2
        return None, None

    def __unicode__(self):
        SPACE = u' '
        _list = (self.left_text, self.context, self.right_text)
        return SPACE.join(_list)

    def forJSON(self):
        _fields = (
            'context',
            'id',
            'left_text',
            'meaning_id',
            'order',
            'right_text',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    class Meta:
        verbose_name = u'контекст значения'
        verbose_name_plural = u'контексты значения'


class Meaning(models.Model, JSONSerializable):

    entry_container = ForeignKey(Entry, blank=True, null=True,
            verbose_name=u'лексема', help_text=u'''Лексема, к которой
            относится значение. Выберите, только если значение не относится
            к словосочетанию.''', related_name='meaning_set')

    collogroup_container = ForeignKey('CollocationGroup', blank=True, null=True,
            verbose_name=u'словосочетание', help_text=u'''Словосочетание,
            к которому относится значение.  Выберите, только если значение не
            относится к конкретной лексеме.''', related_name='meaning_set')

    order = SmallIntegerField(u'порядок следования', blank=True, default=345)
    parent_meaning = ForeignKey('self', verbose_name=u'родительское значение',
                    related_name='child_meaning_set', blank=True, null=True)

    hidden = BooleanField(u'Скрыть значение', help_text=u'''Не отображать
                          данное значение при выводе словарной статьи.''',
                          default=False, editable=False)

    link_to_meaning = ForeignKey('self', verbose_name=u'ссылка на значение',
                    help_text=u'''Если значение должно вместо текста содержать
                    только ссылку на другое значение некоторой лексемы или
                    словосочетания, укажите её в данном поле.''',
                    related_name='ref_meaning_set', blank=True, null=True)

    link_to_entry = ForeignKey(Entry, verbose_name=u'ссылка на лексему',
                    help_text=u'''Если вместо значения должна быть только ссылка
                    на другую словарную статью, укажите её в данном поле.''',
                    related_name='ref_meaning_set', blank=True, null=True)

    link_to_collogroup = ForeignKey('CollocationGroup',
            verbose_name=u'ссылка на словосочетание', help_text=u'''Если вместо
            значения должна быть только ссылка на целое словосочетание.''',
            related_name='ref_meaning_set', blank=True, null=True)

    cf_entries = ManyToManyField(Entry, verbose_name=u'ср. (лексемы)',
                        related_name='cf_meaning_set', blank=True, null=True)

    cf_collogroups = ManyToManyField('CollocationGroup',
                        verbose_name=u'ср. (группы слововосочетаний)',
                        related_name='cf_meaning_set', blank=True, null=True)

    cf_meanings = ManyToManyField('self', verbose_name=u'ср. (значения)',
                        related_name='cf_meaning_set', symmetrical=False,
                        blank=True, null=True)

    @property
    def cfmeanings(self):
        return self.cf_meanings.all()

    @property
    def cfentries(self):
        return self.cf_entries.all()

    @property
    def cfcollogroups(self):
        return self.cf_collogroups.all()

    is_valency = BooleanField(u'содержит управление', default=False)
    metaphorical = BooleanField(u'гимногр.метафора', default=False)
    figurative = BooleanField(u'переносное', default=False)
    meaning = TextField(u'значение', blank=True)

    gloss = TextField(u'пояснение', help_text=u'''Для неметафорических
            употреблений/прямых значений здесь указывается энциклопедическая
            информация. Для метафорических/переносных -- (?) разнообразная
            дополнительная информация, комментарии к употреблению.''',
            blank=True)

    substantivus = BooleanField(u'в роли сущ.', default=False)
    substantivus_type = CharField(u'форма субстантива', max_length=1,
                                  choices=SUBSTANTIVUS_TYPE_CHOICES,
                                  blank=True, default='')
    substantivus_csl = CharField(u'цсл форма', max_length=100,
                                 blank=True, default='')
    @property
    def substantivus_csl_ucs(self):
        lst = self.substantivus_csl.split(u'##')
        for i, elem in enumerate(lst):
            if not elem:
                continue
            if not (i % 2):
                elem = ucs_convert(elem)
                lst[i] = elem
        return u'##'.join(lst)

    @property
    def substantivus_forms(self):
        RE_COMMA = ur',\s*'
        return [ucs_convert(x)
                for x in re.split(RE_COMMA, self.substantivus_csl) if x]

    # только для глаголов
    transitivity = CharField(u'переходность', max_length=1, blank=True,
                             choices=TRANSITIVITY_CHOICES, default='')

    def is_substantivus_type(self, *slugs):
        return any(SUBSTANTIVUS_TYPE_MAP[slug] == self.substantivus_type
                   for slug in slugs)

    additional_info = TextField(u'примечание', help_text=u'''Любая
            дополнительная информация по данному ЗНАЧЕНИЮ. Дополнительная
            информация по примеру на значение или лексеме указывается не здесь,
            а в аналогичных полях при примере и лексеме, соответственно.''',
            blank=True)

    special_case = CharField(u'особые случаи', max_length=1,
            choices=MEANING_SPECIAL_CASES_CHOICES, blank=True, default='')

    def meaning_for_admin(self):
        text = u''
        template = u'[<em>%s</em>] '
        if self.figurative:
            text += template % u'перен.'
        if self.metaphorical:
            text += template % u'гимногр.метаф.'
        if self.substantivus:
            text += template % u'в роли сущ.'
        meaning = self.meaning.strip()
        if meaning:
            text += u'%s ' % meaning
        gloss = self.gloss.strip()
        if gloss:
            text += u'<em>%s</em> ' % gloss
        if self.child_meanings:
            child_meanings = u''
            for m in self.child_meanings:
                child_meanings += u'<li>%s</li>' % m.meaning_for_admin()
            text += u'<ul>%s</ul>' % child_meanings
        return mark_safe(text)

    def examples_for_admin(self):
        text = u''
        for ex in self.examples:
            text += u'<li>%s</li>' % ex.example
        text = u'<ol>%s</ol>' % text
        child_meanings = self.child_meanings
        if child_meanings:
            text2 = u''
            for cm in child_meanings:
                text2 += u'<li>%s</li>' % cm.examples_for_admin()
            if text2:
                text += u'<ul>%s</ul>' % text2
        return mark_safe(text)

    def not_hidden(self):
        host = self.host
        if host:
            return not host.hidden
        return True

    @property
    def examples(self):
        return self.example_set.order_by('order', 'id')

    @property
    def contexts(self):
        return [mc for mc in self.meaningcontext_set.all()
                   if mc.show_in_dictionary]

    @property
    def collogroups(self):
        return self.collocationgroup_set.all().order_by('order', 'id')

    @property
    def collogroups_phraseological(self):
        cgs = list(self.collocationgroup_set.filter(phraseological=True))
        cgs.sort(key=collogroup_sort_key)
        return cgs

    @property
    def collogroups_non_phraseological(self):
        cgs = list(self.collocationgroup_set.exclude(phraseological=True))
        cgs.sort(key=collogroup_sort_key)
        return cgs

    @property
    def child_meanings(self):
        meanings = self.child_meaning_set
        meanings = meanings.filter(parent_meaning=self).order_by('order', 'id')
        return meanings

    ctime = DateTimeField(editable=False, auto_now_add=True)
    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        if self.entry_container:
            return self.entry_container
        else:
            try:
                host_entry = self.collogroup_container.host_entry
            except:
                return None
            else:
                return host_entry

    @property
    def host(self):
        if self.parent_meaning:
            return self.parent_meaning.host
        elif self.entry_container:
            return self.entry_container
        else:
            return self.collogroup_container

    def volume(self, volume=YET_NOT_IN_VOLUMES):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.volume(volume)
        return False

    def starts_with(self, starts_with=ANY_LETTER):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.starts_with(starts_with)
        return False

    _RE1 = re.compile(ur'[\s,;\\/\(\)]*##[^#]*?##[\s,;\\/\(\)]*|[\s,;\\/\(\)]+',
                      re.UNICODE)
    _RE2 = re.compile(ur'[\-'
                      u'\u2010]'
                      ur'л\.$|^с$|^инф\.$|^придат\.$|^прям\.$|^речью$',
                      re.UNICODE)  # NOTE: В py3 нельзя использовать юникодные
            # экранирующие последовательнсти в сырых строках. \u2010 --
            # неразрывный дефис.

    def looks_like_valency(self, host_entry):
        if host_entry is None:
            return False
        if not host_entry.is_part_of_speech('verb', 'preposition'):
            return False
        if not self.parent_meaning:
            return False
        if self.is_valency:
            return False
        meaning = self.meaning.strip()
        gloss = self.gloss.strip()
        if not meaning and gloss:  #::AUHACK:: Авторы иногда помещают
            # информацию об управлении в поле gloss, чтобы оно в статье
            # отображалось курсивом. Это авторский хак. По нормальному
            # управление должно быть в поле meaning, а в поле gloss при
            # этом может быть комментарий к модели управления.
            string = gloss
        else:
            string = meaning
        words = [w for w in self._RE1.split(string) if w]
        if len(words) > 0 and all(self._RE2.search(w) for w in words):
            return True

    def save(self, without_mtime=False, *args, **kwargs):
        host_entry = self.host_entry
        if self.looks_like_valency(host_entry):
            if self.gloss.strip() and not self.meaning.strip():  #::AUHACK::
                self.meaning = self.gloss
                self.gloss = u''
            self.is_valency = True
        super(Meaning, self).save(*args, **kwargs)
        if without_mtime:
            return
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Meaning, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          m2 = self
          m2.pk = None
          if 'entry' in kwargs and 'collogroup' not in kwargs:
              m2.entry_container = kwargs['entry']
          if 'collogroup' in kwargs:
              m2.collogroup_container = kwargs['collogroup']
          m2.save()
          m1 = Meaning.objects.get(pk=id1)
          m2m = ('meaningcontext_set', 'example_set', 'collocationgroup_set')
          kwargs['meaning'] = m2
          return _double_check(m1, m2, m2m=m2m, kwargs=kwargs, model=Meaning)
        return None, None

    def get_url_fragment(self):
        return 'm{0}'.format(self.id)

    def __unicode__(self):
        return self.meaning

    def forJSON(self):
        _fields = (
            'additional_info',
            'collogroup_container_id',
            'entry_container_id',
            'figurative',
            'gloss',
            'hidden',
            'id',
            'meaning',
            'metaphorical',
            'order',
            'parent_meaning_id',
            'substantivus',
            'substantivus_type',
        )
        dct = dict((key, self.__dict__[key]) for key in _fields)
        dct['contexts'] = [c.forJSON() for c in self.meaningcontext_set.all()]
        dct['collogroups'] = [c.forJSON() for c in self.collogroups]
        dct['meanings'] = [m.forJSON() for m in self.child_meanings]
        dct['examples'] = [e.forJSON() for e in self.examples]
        return dct

    class Meta:
        verbose_name = u'значение'
        verbose_name_plural = u'ЗНАЧЕНИЯ'
        ordering = ('id',)


class Example(models.Model, JSONSerializable):

    meaning = ForeignKey(Meaning, verbose_name=u'значение',
              help_text=u'Значение, к которому относится данный пример.',
              blank=True, null=True)

    entry = ForeignKey(Entry, blank=True, null=True)
    collogroup = ForeignKey('CollocationGroup', blank=True, null=True)

    order = SmallIntegerField(u'порядок следования', blank=True, default=345)
    hidden = BooleanField(u'Скрыть пример', help_text=u'''Не отображать данный
                          пример при выводе словарной статьи.''',
                          default=False, editable=False)

    example = TextField(u'пример')
    ts_example = TextField(default=u'')

    @property
    def example_ucs(self):
        return ucs_convert(self.example)

    context = TextField(u'широкий контекст',
                  help_text=u'Более широкий контекст для примера', blank=True)

    @property
    def context_ucs(self):
        c = self.context
        e = ucs_convert(self.example)
        if c:
            c = ucs_convert(c)
            x, y, z = c.partition(e)
            if y:
                # Разбиение дало положительный результат,
                # в "y" помещён сам пример.
                return (x, y, z)
        return (u'', e, u'')

    address_text = CharField(u'адрес', max_length=300, blank=True)

    @property
    def greek_equivs(self):
        return self.greq_set.all().order_by('order', 'id')

    @property
    def translations(self):
        return self.translation_set.all().order_by('order', 'id')

    def greek_equivs_with_numbers(self, show_info=False):
        # Если не надо отображать авторские комментарии, то выводим
        # только реальные греч. параллели с заполненным полем unitext,
        # остальные пропускаем.
        if show_info:
            lst = list(self.greek_equivs)
        else:
            lst = [ge for ge in self.greek_equivs if ge.unitext.strip()]
        L = len(lst)
        if L == 0:
            groups = []
        elif L == 1:
            groups = [(lst[0], 1)]
        else:
            groups = []
            ge_prev = lst[0]
            n = 1
            for ge in lst[1:]:
                if ge.unitext == ge_prev.unitext:
                    n += 1
                else:
                    groups.append((ge_prev, n))
                    ge_prev = ge
                    n = 1
            groups.append((ge_prev, n))
        assert sum(x[1] for x in groups) == L, u'Число параллелей д.б постоянным'
        return groups

    audited = BooleanField(u'Пример прошел проверку или взят на проверку',
                           default=False)
    audited_time = DateTimeField(u'Когда пример был проверен', blank=True,
            editable=False, null=True)

    note = TextField(u'комментарий', help_text=u'''Дополнительная
            информация по данному примеру, которая будет видна рядовому
            пользователю словаря''', blank=True)

    additional_info = TextField(u'примечание', help_text=u'''Любая
            дополнительная информация по данному ПРИМЕРУ. Дополнительная
            информация по значению или лексеме указывается не здесь,
            а в аналогичных полях при значении и лексеме, соответственно.''',
            blank=True)

    GREEK_EQ_LOOK_FOR = u'L'  # Следует найти греческие параллели для примера
    GREEK_EQ_STOP = u'S'  # Греческие параллели не нужны
    GREEK_EQ_CHECK_ADDRESS = u'C'
        # Необходимо уточнить адрес примера, чтобы грецист смог найти пример
    GREEK_EQ_NOT_FOUND = u'N'  # Греч.параллель для примера найти не удалось
    GREEK_EQ_FOUND = u'F'  # Греч.параллель для примера найдена
    GREEK_EQ_POSTPONED = u'P'  # Нахождение греч. параллели отложено, например,
        # потому что у грециста в данный момент нет греч. текста, но впоследствии
        # может появиться.
    GREEK_EQ_MEANING = u'M'
        # Греч.параллели для примера нужны, чтобы определить значение слова
    GREEK_EQ_URGENT = u'U'  # Греч.параллели для примера нужны в срочном порядке

    GREEK_EQ_STATUS = (
        (GREEK_EQ_LOOK_FOR, u'следует найти'),
        (GREEK_EQ_STOP, u'не нужны'),
        (GREEK_EQ_CHECK_ADDRESS, u'уточнить адрес'),
        (GREEK_EQ_NOT_FOUND, u'найти не удалось'),
        (GREEK_EQ_POSTPONED, u'когда-нибудь позже, отложенные на потом'),
        (GREEK_EQ_FOUND, u'найдены'),
        (GREEK_EQ_MEANING, u'необходимы для опр-я значения'),
        (GREEK_EQ_URGENT, u'срочное'),
    )

    greek_eq_status = CharField(u'параллели', max_length=1,
            choices=GREEK_EQ_STATUS, default=GREEK_EQ_LOOK_FOR)

    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        if self.entry:
            return self.entry
        else:
            try:
                host_entry = self.meaning.host_entry
            except:
                return None
            else:
                return host_entry

    @property
    def host(self):
        if self.collogroup:
            return self.collogroup
        else:
            if self.meaning:
                return self.meaning.host
            else:
                return self.entry

    def volume(self, volume=YET_NOT_IN_VOLUMES):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.volume(volume)
        return False

    def starts_with(self, starts_with=ANY_LETTER):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.starts_with(starts_with)
        return False

    def example_for_admin(self):
        text = u''
        return mark_safe(text)

    def ts_convert(self):
        RE = re.compile(
                u'[^'
                u'абвгдеєжѕзийіклмноѻпрстѹꙋуфхѿцчшщъыьѣюꙗѡѽѧѯѱѳѵ'
                u'АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸꙊУФХѾЦЧШЩЪЫЬѢЮꙖѠѼѦѮѰѲѴ'
                ur'\~\'\`\^ı'
                u']+')
        ts_text = u''
        for word in re.split(RE, self.example):
            ts_word = word[:1].lower()
            if len(word) > 2:
                ts_word += word[1:-1]
            if len(word) > 1 and word[-1].lower() != u'ъ':
                ts_word += word[-1]
            ts_text += ts_word
        self.ts_example = civilrus_convert(ts_text)

    def save(self, without_mtime=False, *args, **kwargs):
        self.ts_convert()
        host_entry = self.host_entry
        if host_entry is not None:
            self.entry = host_entry
        host = self.host
        if host and 'base_meaning_id' in host.__dict__:
            self.collogroup = host
        super(Example, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Example, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          ex2 = self
          ex2.pk = None
          if 'meaning' in kwargs:
              ex2.meaning = kwargs['meaning']
          if 'entry' in kwargs:
              ex2.entry = kwargs['entry']
          if 'collogroup' in kwargs:
              ex2.collogroup = kwargs['collogroup']
          ex2.save()
          ex1 = Example.objects.get(pk=id1)
          m2m = ('greq_set', 'translation_set')
          kwargs['example'] = ex2
          return _double_check(ex1, ex2, m2m=m2m, kwargs=kwargs, model=Example)
        return None, None

    def forJSON(self):
        _fields = (
            'additional_info',
            'address_text',
            'collogroup_id',
            'context',
            'entry_id',
            'example',
            'greek_eq_status',
            'hidden',
            'id',
            'meaning_id',
            'note',
            'order',
        )
        dct = dict((key, self.__dict__[key]) for key in _fields)
        dct['greqs'] = [ge.forJSON() for ge in self.greek_equivs]
        dct['translations'] = [t.forJSON() for t in self.translations]
        return dct

    def forHellinistJSON(self):
        data = {
            'id': self.id,
            'triplet': self.context_ucs,
            'antconc': self.context.strip() or self.example,
            'example': self.example,
            'address': self.address_text,
            'status': self.greek_eq_status,
            'audited': self.audited_time and self.audited,
            'comment': self.additional_info,
            'greqs': [greq.forJSON() for greq in self.greek_equivs],
        }
        return data

    def toHellinistJSON(self):
        return json.dumps(self.forHellinistJSON(),
                          ensure_ascii=False, separators=(',', ':'))

    def get_translations(self, fragmented, hidden):
        translations = self.translation_set.filter(fragmented=fragmented,
                hidden=hidden)
        if fragmented:
            translations = translations.order_by('fragment_end', 'order', 'id')
            data = defaultdict(list)
            for t in translations:
                if t.translation.strip():
                    data[t.fragment_end].append(t)
        else:
            data = tuple(t for t in translations.order_by('order', 'id')
                           if t.translation.strip())
        return data

    def __unicode__(self):
        return u'(%s) %s' % (self.address_text, self.example)

    class Meta:
        verbose_name = u'пример'
        verbose_name_plural = u'ПРИМЕРЫ'
        ordering = ('id',)


class Translation(models.Model, JSONSerializable):

    for_example = ForeignKey(Example, related_name='translation_set')
    fragmented = BooleanField(u'перевод только части примера', default=False)
    fragment_start = SmallIntegerField(u'номер слова начала фрагмента',
            blank=True, default=1)
    fragment_end = SmallIntegerField(u'номер слова конца фрагмента',
            blank=True, default=1000)
    order = SmallIntegerField(u'порядок следования', blank=True, default=345)
    hidden = BooleanField(u'скрывать перевод', default=True,
            help_text=u'отображать перевод только в комментариях для авторов')
    translation = TextField(u'перевод')
    additional_info = TextField(u'примечание', blank=True)

    @property
    def host_entry(self):
        try:
            host_entry = self.for_example.host_entry
        except:
            return None
        else:
            return host_entry

    @property
    def host(self):
        try:
            host = self.for_example.host
        except:
            return None
        else:
            return host

    def forJSON(self):
        _fields = (
            'additional_info',
            'for_example_id',
            'fragmented',
            'fragment_start',
            'fragment_end',
            'hidden',
            'id',
            'order',
            'translation',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    def save(self, without_mtime=False, *args, **kwargs):
        super(Translation, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Translation, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          t2 = self
          t2.pk = None
          if 'example' in kwargs:
              t2.for_example = kwargs['example']
          t2.save()
          t1 = Translation.objects.get(pk=id1)
          return t1, t2
        return None, None

    def __unicode__(self):
        if self.fragmented:
            return u'(%s, %s) %s' % (self.fragment_start, self.fragment_end,
                                     self.translation)
        else:
            return self.translation

    class Meta:
        verbose_name = u'перевод'
        verbose_name_plural = u'ПЕРЕВОДЫ'
        ordering = ('id',)


class CollocationGroup(models.Model, JSONSerializable):

    base_entry = ForeignKey(Entry, verbose_name=u'лексема',
            help_text=u'''Лексема, при которой будет стоять словосочетание.
            Если есть возможность указать конкретное значение, лучше указать
            вместо лексемы её конкретное значение.''',
            related_name='collocationgroup_set', blank=True, null=True)

    base_meaning = ForeignKey(Meaning, verbose_name=u'значение',
            help_text=u'''Значение, при котором будет стоять словосочетание.''',
            related_name='collocationgroup_set', blank=True, null=True)

    phraseological = BooleanField(u'фразеологизм', default=False)

    link_to_entry = ForeignKey(Entry, verbose_name=u'ссылка на лексему',
            help_text=u'''Если вместо значений словосочетания должна быть
            только ссылка на словарную статью, укажите её в данном поле.''',
            related_name='ref_collogroup_set', blank=True, null=True)

    link_to_meaning = ForeignKey('Meaning', verbose_name=u'ссылка на значение',
            help_text=u'''Если вместо значений словосочетания должна быть
            только ссылка на опредленное значение лексемы или словосочетания,
            укажите его в данном поле.''', related_name='ref_collogroup_set',
            blank=True, null=True)

    cf_entries = ManyToManyField(Entry, verbose_name=u'ср. (лексемы)',
            related_name='cf_collogroup_set', blank=True, null=True)

    cf_meanings = ManyToManyField(Meaning, verbose_name=u'ср. (значения)',
            related_name='cf_collogroup_set', blank=True, null=True)

    order = SmallIntegerField(u'порядок следования', blank=True, default=345)
    ctime = DateTimeField(editable=False, auto_now_add=True)
    mtime = DateTimeField(editable=False, auto_now=True)
    additional_info = TextField(u'примечание', blank=True)
    hidden = BooleanField(u'Скрыть словосочетание', help_text=u'''Не отображать
            словосочетание в статье.''', default=False, editable=False)

    objects = WithoutHiddenManager()
    objects_all = models.Manager()

    @property
    def collocations(self):
        return self.collocation_set.all().order_by('order', 'id')

    @property
    def host_entry(self):
        if self.base_entry:
            return self.base_entry
        elif self.base_meaning:
            try:
                host_entry = self.base_meaning.host_entry
            except:
                return None
            else:
                return host_entry

    host = host_entry

    def volume(self, volume=YET_NOT_IN_VOLUMES):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.volume(volume)
        return False

    def starts_with(self, starts_with=ANY_LETTER):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.starts_with(starts_with)
        return False

    def meanings_for_admin(self):
        meanings = self.meanings
        if len(meanings) == 0:
            text = u''
        elif len(meanings) == 1:
            text = meanings[0].meaning_for_admin()
        else:
            text = text2 = u''
            for m in meanings:
                text2 += u'<li>%s</li>' % m.meaning_for_admin()
            text += u'<ol>%s</ol>' % text2
        if self.metaph_meanings:
            text2 = u''
            for m in self.metaph_meanings:
                text2 += u'<li>%s</li>' % m.meaning_for_admin()
            text += u'<ul>%s</ul>' % text2
        return mark_safe(text)

    def examples_for_admin(self):
        text = u''
        for m in self.meanings:
            text += m.examples_for_admin()
            if m.child_meanings:
                text2 = u''
                for cm in m.child_meanings:
                    text2 += u'<li>%s</li>' % cm.examples_for_admin()
                if text2:
                    text += u'<ul>%s</ul>' % text2
        if self.metaph_meanings:
            text2 = u''
            for m in self.metaph_meanings:
                text2 += u'<li>%s</li>' % m.examples_for_admin()
            text += u'<ul>%s</ul>' % text2
        return mark_safe(text)

    meanings = property(meanings)
    metaph_meanings = property(metaph_meanings)
    all_meanings = property(all_meanings)
    has_meanings = property(has_meanings)

    def get_url_fragment(self):
        return 'cg{0}'.format(self.id)

    def save(self, without_mtime=False, *args, **kwargs):
        super(CollocationGroup, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(CollocationGroup, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          cg2 = self
          cg2.pk = None
          if 'entry' in kwargs and 'meaning' not in kwargs:
              cg2.base_entry = kwargs['entry']
          if 'meaning' in kwargs:
              cg2.base_meaning = kwargs['meaning']
          cg2.save()
          cg1 = CollocationGroup.objects.get(pk=id1)
          m2m = ('collocation_set', 'meaning_set')
          kwargs['collogroup'] = cg2
          cg1, cg2 = _double_check(cg1, cg2, m2m=m2m, kwargs=kwargs,
                                   model=CollocationGroup)
          # Очищаем kwargs от всех накопившихся ключей кроме необходимых
          kwargs = {
              'entry': kwargs['entry'],
              'collogroup': kwargs['collogroup'],
              'object_map': kwargs['object_map'],
          }
          # Дублируем только те примеры, которые относятся к словосочетанию
          # в целом, но не к значению и не в целом ко статье.
          for ex1 in cg1.example_set.filter(meaning_id__isnull=True):
              ex1, ex2 = ex1.make_double(**kwargs)
          return cg1, cg2
        return None, None

    def forJSON(self):
        _fields = (
            'base_entry_id',
            'base_meaning_id',
            'id',
            'order',
            'additional_info',
        )
        dct = dict((key, self.__dict__[key]) for key in _fields)
        dct['collocations'] = [c.forJSON() for c in self.collocations]
        dct['meanings'] = [m.forJSON() for m in self.all_meanings]
        dct['unsorted_examples'] = [e.forJSON()
                for e in self.example_set.filter(meaning__isnull=True)]
        return dct

    @property
    def civil_equivalent(self):
        return u'; '.join(c.civil_equivalent for c in self.collocations)

    class Meta:
        verbose_name = u'группа словосочетаний'
        verbose_name_plural = u'ГРУППЫ СЛОВОСОЧЕТАНИЙ'
        ordering = ('-id',)


class Collocation(models.Model, JSONSerializable):

    collogroup = ForeignKey(CollocationGroup,
                            verbose_name=u'группа словосочетаний',
                            related_name='collocation_set')

    collocation = CharField(u'словосочетание', max_length=200)

    @property
    def collocation_ucs(self):
        lst = self.collocation.split(u'##')
        for i, elem in enumerate(lst):
            if not elem:
                continue
            if not (i % 2):
                elem = ucs_convert(elem)
                lst[i] = elem
        return u'##'.join(lst)

    civil_equivalent = CharField(u'гражданское написание', max_length=350,
                                 blank=True)
    civil_inverse = CharField(u'гражд. инв.', max_length=350)

    order = SmallIntegerField(u'порядок следования', blank=True, default=345)

    @property
    def etymologies(self):
        etyms = self.etymology_set.filter(language__in=ETYMOLOGY_LANGUAGES)
        etyms = list(etyms)
        etyms.sort(key=lambda x:(bool(x.etymon_to), x.order, x.id))
        return etyms

    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        try:
            host_entry = self.collogroup.host_entry
        except:
            return None
        else:
            return host_entry

    @property
    def host(self):
        return self.collogroup

    def save(self, without_mtime=False, *args, **kwargs):
        self.civil_equivalent = civilrus_convert(self.collocation)
        self.civil_inverse = self.civil_equivalent[::-1]
        super(Collocation, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Collocation, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          c2 = self
          c2.pk = None
          if 'collogroup' in kwargs:
              c2.collogroup = kwargs['collogroup']
          c2.save()
          c1 = Collocation.objects.get(pk=id1)
          m2m = ('etymology_set',)
          kwargs['collocation'] = c2
          return _double_check(c1, c2, m2m=m2m, kwargs=kwargs, model=Collocation)
        return None, None

    def __unicode__(self):
        return self.collocation

    def forJSON(self):
        _fields = (
            'civil_equivalent',
            'collocation',
            'collogroup_id',
            'id',
            'order',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    class Meta:
        verbose_name = u'словосочетание'
        verbose_name_plural = u'ОТДЕЛЬНЫЕ СЛОВОСОЧЕТАНИЯ'
        ordering = ('id',)


class GreekEquivalentForExample(models.Model, JSONSerializable):

    for_example = ForeignKey(Example, related_name='greq_set')
    unitext = CharField(u'греч. параллель (Unicode)', max_length=100,
                        blank=True)

    mark = CharField(u'грамматическая помета', max_length=20, blank=True)

    source = CharField(u'документальный источник', help_text=u'''Например,
                       Септуагинта или, более узко, разные редакции одного
                       текста.''', max_length=40, blank=True)

    position = SmallIntegerField(u'позиция в примере', blank=True, default=1000,
            help_text=u'Номер слова, после которого следует поставить перевод.',
            null=True)

    initial_form = CharField(u'начальная форма лексемы',
                             max_length=100, blank=True)
    initial_form_phraseology = CharField(u'начальная форма фразеологизма',
                             max_length=100, blank=True)

    note = TextField(u'комментарий', help_text=u'''Любая дополнительная
                     информация по данному греческому эквиваленту, которая
                     будет включена в текст статьи.''',
                     blank=True)

    additional_info = TextField(u'примечание', help_text=u'''Любая
                                дополнительная информация по данному
                                греческому эквиваленту, которая в текст
                                статьи не войдет''', blank=True)

    aliud = BooleanField(u'в греч. иначе', default=False)
    mtime = DateTimeField(editable=False, auto_now=True)
    order = SmallIntegerField(u'порядок следования', blank=True, default=345)

    @property
    def is_aliud_latin(self):
        text = self.unitext
        return self.aliud and re.sub('[a-zA-Z]', '', text) != text

    @property
    def host_entry(self):
        try:
            host_entry = self.for_example.host_entry
        except:
            return None
        else:
            return host_entry

    @property
    def host(self):
        try:
            host = self.for_example.host
        except:
            return None
        else:
            return host

    def save(self, without_mtime=False, *args, **kwargs):
        self.unitext = self.unitext.strip()
        super(GreekEquivalentForExample, self).save(*args, **kwargs)
        example = self.for_example
        if self.unitext.strip() and example.greek_eq_status in (
                Example.GREEK_EQ_LOOK_FOR,
                Example.GREEK_EQ_NOT_FOUND,
                Example.GREEK_EQ_CHECK_ADDRESS,
                Example.GREEK_EQ_MEANING,
                Example.GREEK_EQ_URGENT):
            example.greek_eq_status = Example.GREEK_EQ_FOUND
            example.save(without_mtime=without_mtime)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(GreekEquivalentForExample, self).delete(*args, **kwargs)
        if not self.for_example.greek_equivs.exists():
            example = self.for_example
            example.greek_eq_status = Example.GREEK_EQ_LOOK_FOR
            example.save(without_mtime=without_mtime)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          ge2 = self
          ge2.pk = None
          if 'example' in kwargs:
              ge2.for_example = kwargs['example']
          ge2.save()
          ge1 = GreekEquivalentForExample.objects.get(pk=id1)
          return ge1, ge2
        return None, None

    def forJSON(self):
        _fields = (
            'additional_info',
            'aliud',
            'for_example_id',
            'id',
            'initial_form',
            'initial_form_phraseology',
            'mark',
            'note',
            'position',
            'source',
            'unitext',
            'order',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    class Meta:
        verbose_name = u'греческая параллель для примера'
        verbose_name_plural = u'греческие параллели'
        ordering = ('order', 'id')


class OrthographicVariant(models.Model, JSONSerializable):

    # словарная статья, к которой относится данный орф. вариант
    entry = ForeignKey(Entry, related_name='orthographic_variants', blank=True,
                       null=True)
    parent = ForeignKey('self', related_name='children', blank=True, null=True)
    without_accent = BooleanField(u'без ударения', default=False)
    reconstructed = BooleanField(u'реконструирован', default=False)
    questionable = BooleanField(u'реконструкция вызывает сомнения', default=False)
    untitled_exists = BooleanField(u'Вариант без титла представлен в текстах',
                                   default=False)
    @property
    def childvars(self):
        childvars = self.children.all()

        # Проверяем есть ли титла в текущей словоформе.
        # Для этого обрезаем начальные пробелы и знаки снятия придыхания.
        var = self.idem.lstrip(u' =')
        # Удаляем первый символ, т.к. он может иметь верхний регистр.
        var = var[1:]
        # Смотрим, есть ли титла, при этом намеренно исключаем из поиска
        # паерки (ЪЬ).
        r = re.compile(ur'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
        has_no_title = not r.search(var)

        if self.untitled_exists and has_no_title:
            childvars = tuple(childvars) + (self,)
        return childvars

    # сам орфографический вариант
    idem = CharField(u'написание', max_length=50)
    use = CharField(u'использование', max_length=50, help_text=u'''
                    Информация о том, с какими значениями данный вариант
                    связан. Разные варианты написания могут коррелировать
                    с разными значениями, как в случае слов богъ/бг~ъ,
                    агг~лъ/аггелъ.''', default=u'')
    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    @property
    def idem_letter_ucs(self):
        return ucs_convert_affix(self.idem.lower())

    order = SmallIntegerField(u'порядок следования', blank=True, default=345)
    no_ref_entry = BooleanField(u'Не делать отсылочной статьи', default=False)
    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        return self.entry

    host = host_entry

    def save(self, without_mtime=False, *args, **kwargs):
        if self.questionable and not self.reconstructed:
            self.reconstructed = True
        super(OrthographicVariant, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(OrthographicVariant, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          ov2 = self
          ov2.pk = None
          if 'entry' in kwargs:
              ov2.entry = kwargs['entry']
          ov2.save()
          ov1 = OrthographicVariant.objects.get(pk=id1)
          return ov1, ov2
        return None, None

    def __unicode__(self):
        return self.idem

    def forJSON(self):
        _fields = (
            'entry_id',
            'parent_id',
            'id',
            'idem',
            'reconstructed',
            'questionable',
            'order',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    class Meta:
        verbose_name = u'вариант'
        verbose_name_plural = u'варианты'
        ordering = ('order', 'id')


class Participle(models.Model, JSONSerializable):

    # словарная статья, к которой относится данная словоформа
    entry = ForeignKey(Entry, blank=True, null=True)

    PARTICIPLE_CHOICES = PARTICIPLE_CHOICES

    tp = CharField(u'тип причастия', max_length=2, choices=PARTICIPLE_CHOICES)
    idem = CharField(u'словоформа', max_length=50)

    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    order = SmallIntegerField(u'порядок следования', blank=True, default=345)
    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        return self.entry

    host = host_entry

    def save(self, without_mtime=False, *args, **kwargs):
        super(Participle, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Participle, self).delete(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None:
            host_entry.save(without_mtime=without_mtime)

    def make_double(self, **kwargs):
        with transaction.atomic():
          id1 = self.pk
          p2 = self
          p2.pk = None
          if 'entry' in kwargs:
              p2.entry = kwargs['entry']
          p2.save()
          p1 = Participle.objects.get(pk=id1)
          return p1, p2
        return None, None

    def __unicode__(self):
        return self.idem

    def forJSON(self):
        _fields = (
            'entry_id',
            'id',
            'idem',
            'order',
            'tp',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    class Meta:
        verbose_name = u'причастие'
        verbose_name_plural = u'причастия'
        ordering = ('order', 'id')



def get_max_lengths(Model):
    return {f.name:f.max_length
            for f in Model._meta.fields
            if isinstance(f, CharField) and not f.choices}

MAX_LENGTHS = {}
Models = (
    Collocation,
    CollocationGroup,
    Entry,
    Etymology,
    Example,
    GreekEquivalentForExample,
    Meaning,
    MeaningContext,
    OrthographicVariant,
    Participle,
    Translation,
)
for Model in Models:
    x = get_max_lengths(Model)
    if x:
        MAX_LENGTHS[Model.__name__] = x

try:
    LETTERS = set(e.civil_equivalent.lstrip(u' =')[0].lower()
                  for e in Entry.objects.all())
except (OperationalError, ProgrammingError):
    LETTERS = []
else:
    LETTERS = list(LETTERS)
    LETTERS.sort()
