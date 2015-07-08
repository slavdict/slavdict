# -*- coding: UTF-8 -*-
import datetime
import json

from django.db import models
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import PositiveIntegerField
from django.db.models import PositiveSmallIntegerField
from django.db.models import SmallIntegerField
from django.db.models import TextField

from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import antconc_ucs8
from hip2unicode.conversions import antconc_ucs8_without_aspiration
from hip2unicode.conversions import antconc_civilrus

from slavdict.custom_user.models import CustomUser

compiled_conversion_with_aspiration = compile_conversion(
        antconc_ucs8.conversion)
compiled_conversion_without_aspiration = compile_conversion(
        antconc_ucs8_without_aspiration.conversion)
compiled_conversion_civil = compile_conversion(antconc_civilrus.conversion)


def ucs_convert(text):
    return convert(text, compiled_conversion_with_aspiration)


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
        return convert(text, compiled_conversion_without_aspiration)
    return text


def civilrus_convert(word):
    return convert(word, compiled_conversion_civil)


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
)
PART_OF_SPEECH_MAP = {
    'noun': 'a',
    'adjective': 'b',
    'pronoun': 'c',
    'verb': 'd',
    'participle': 'e',
    'adverb': 'f',
    'conjunction': 'g',
    'adposition': 'h',
    'particle': 'i',
    'interjection': 'j',
    'number': 'k',
    'letter': 'l',
}

TANTUM_CHOICES = (
    ('s', u'только ед.'),
    ('d', u'только дв.'),
    ('p', u'только мн.'),
)
TANTUM_MAP = {
    'singulareTantum': 's',
    'dualeTantum': 'd',
    'pluraleTantum': 'p',
}

GENDER_CHOICES = (
    ('m', u'м.'),
    ('f', u'ж.'),
    ('n', u'ср.'),
)
GENDER_MAP = {
    'masculine': 'm',
    'feminine': 'f',
    'neutral': 'n',
}

ONYM_CHOICES = (
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
    ('t', u'перех.'),
    ('i', u'неперех.'),
)
TRANSITIVITY_MAP = {
    'transitive': 't',
    'intransitive': 'i',
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
    'created': 'c',
    'inWork': 'w',
    'greek': 'g',
    'finished': 'f',
    'beingEdited': 'e',
    'approved': 'a',
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
    'greek': 'a',
    'hebrew': 'b',
    'akkadian': 'c',
    'aramaic': 'd',
    'armenian': 'e',
    'georgian': 'f',
    'coptic': 'g',
    'latin': 'h',
    'syriac': 'i',
}
ETYMOLOGY_LANGUAGES = [
    LANGUAGE_MAP['greek'],
    LANGUAGE_MAP['latin'],
]
LANGUAGE_CSS = {
        LANGUAGE_MAP['greek']: 'grec',
        LANGUAGE_MAP['hebrew']: 'hebrew',
        LANGUAGE_MAP['akkadian']: 'akkadian',
        LANGUAGE_MAP['aramaic']: 'aramaic',
        LANGUAGE_MAP['armenian']: 'armenian',
        LANGUAGE_MAP['georgian']: 'georgian',
        LANGUAGE_MAP['coptic']: 'coptic',
        LANGUAGE_MAP['latin']: '',
        LANGUAGE_MAP['syriac']: 'syriac',
}
LANGUAGE_TRANSLIT_CSS = {
        LANGUAGE_MAP['greek']: '',
        LANGUAGE_MAP['hebrew']: 'hebrew-translit',
        LANGUAGE_MAP['akkadian']: '',
        LANGUAGE_MAP['aramaic']: 'aramaic-translit',
        LANGUAGE_MAP['armenian']: '',
        LANGUAGE_MAP['georgian']: '',
        LANGUAGE_MAP['coptic']: '',
        LANGUAGE_MAP['latin']: '',
        LANGUAGE_MAP['syriac']: 'syriac-translit',
}

SUBSTANTIVUS_TYPE_CHOICES = (
    ('a', u'ср.ед.'),
    ('b', u'ср.мн.'),
    ('c', u'м.ед.'),
    ('d', u'м.мн.'),
    ('e', u'ж.ед.'),
    ('f', u'ж.мн.'),
)
SUBSTANTIVUS_TYPE_MAP = {
    'n.sg.': 'a',
    'n.pl.': 'b',
    'm.sg.': 'c',
    'm.pl.': 'd',
    'f.sg.': 'e',
    'f.pl.': 'f',
}

INFL_NUMBER = (
    ('1', u'ед.ч.'),
    ('2', u'дв.ч.'),
    ('8', u'мн.ч.'),
)
INFL_CASE = (
    ('v', u'Зват.'),
    ('n', u'Им.'),
    ('g', u'Род.'),
    ('d', u'Дат.'),
    ('a', u'Вин.'),
    ('i', u'Твор.'),
    ('p', u'Предл.'),
)
INFL_GENDER = GENDER_CHOICES

INFL_SHORTNESS = (
    ('s', u'краткая форма'),
    ('f', u'полная форма'),
)
INFL_COMPARISON = (
    ('p', u'положит.'),
    ('c', u'компар.'),
    ('s', u'превосх.'),
)
INFL_VOICE = (
    ('a', u'актив.'),
    ('p', u'пассив.'),
)
INFL_MOOD = (
    ('f', u'инфинитив'),
    ('i', u'изъявит.'),
    ('c', u'сослагат.'),
    ('m', u'повелит.'),
)
INFL_PERSON = (
    ('1', u'1-е лицо'),
    ('2', u'2-е лицо'),
    ('3', u'3-е лицо'),
)

class WithoutHiddenManager(models.Manager):
    def get_queryset(self):
        return super(WithoutHiddenManager,
                     self).get_queryset().filter(hidden=False)

class Entry(models.Model):

    civil_equivalent = CharField(u'гражд. написание', max_length=50)
    civil_inverse = CharField(u'гражд. инв.', max_length=50)

    @property
    def orth_vars(self):
        return self.orthographic_variants.all()

    @property
    def orth_vars_refs(self):
        return self.orthographic_variants.filter(no_ref_entry=False)

    reconstructed_headword = BooleanField(u'Заглавное слово реконструировано',
            default=False)

    questionable_headword = BooleanField(u'''Реконструкция заглавного слова
            вызывает сомнения''', default=False)

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

    def is_part_of_speech(self, slug):
        return PART_OF_SPEECH_MAP[slug] == self.part_of_speech

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

    # только для прилагательных
    short_form = CharField(u'краткая форма', help_text=u'''Если Вы указываете
                           не всё слово, а только его часть, предваряйте её
                           дефисом.''', max_length=50, blank=True)

    @property
    def short_form_ucs_wax(self):
        return ucs_affix_or_word(self.short_form)

    possessive = BooleanField(u'притяжательное', default=False,
                              help_text=u'Притяжательное прилагательное.')

    # только для глаголов
    transitivity = CharField(u'переходность', max_length=1, blank=True,
                             choices=TRANSITIVITY_CHOICES, default='')

    def is_transitivity(self, slug):
        return TRANSITIVITY_MAP[slug] == self.transitivity

    sg1 = CharField(u'форма 1 ед.', max_length=50, blank=True,
                    help_text=u'''Целая словоформа или окончание. В случае
                    окончания первым символом должен идти дефис.''')

    @property
    def sg1_ucs_wax(self):
        return ucs_affix_or_word(self.sg1)

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
        etyms = etyms.filter(etymon_to__isnull=True).order_by('order', 'id')
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

    @models.permalink
    def get_absolute_url(self):
        return ('single_entry_url', [str(self.id)])

    def save(self, without_mtime=False, *args, **kwargs):
        self.civil_inverse = self.civil_equivalent[::-1]
        if not without_mtime:
            self.mtime = datetime.datetime.now()
        super(Entry, self).save(*args, **kwargs)

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
            'questionable_headword',
            'reconstructed_headword',
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

    objects = WithoutHiddenManager()
    objects_all = models.Manager()

    class Meta:
        verbose_name = u'словарная статья'
        verbose_name_plural = u'СЛОВАРНЫЕ СТАТЬИ'
        ordering = ('-id',)


class Etymology(models.Model):

    entry = ForeignKey(Entry, verbose_name=u'словарная статья',
                help_text=u'''Словарная статья, к которой относится данная
                этимология.''', blank=True, null=True)

    collocation = ForeignKey('Collocation', verbose_name=u'словосочетание',
                help_text=u'''Словосочетание, к которому относится данная
                этимология.''', blank=True, null=True)

    order = SmallIntegerField(u'порядок следования', blank=True, default=0)

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
    corrupted = BooleanField(u'текст испорчен', default=False)
    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        if self.entry:
            return self.entry
        else:
            return self.collocation.host_entry

    @property
    def host(self):
        if self.entry:
            return self.entry
        else:
            return self.collocation

    def save(self, without_mtime=False, *args, **kwargs):
        super(Etymology, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Etymology, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def __unicode__(self):
        return u'%s %s %s' % (self.get_language_display(), self.entry,
                              self.translit)
    def forJSON(self):
        _fields = (
            'additional_info',
            'collocation_id',
            'corrupted',
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


class QuasiGoodManager(models.Manager):
    def get_queryset(self):
        X = u''
        PL = u'мн.'
        qs = super(QuasiGoodManager, self).get_queryset()
        # Оставляем в выборке только те контексты значений, которые содержат
        # либо только цсл. текст, либо только помету "мн."
        qs = qs.extra(where=['''
            (context!=%s AND left_text=%s AND right_text=%s) OR
            (context=%s AND (left_text=%s OR right_text=%s))
            '''], params=[X] * 4 + [PL] * 2)
        return qs

class MeaningContext(models.Model):

    meaning = ForeignKey('Meaning', verbose_name=u'значение')
    order = SmallIntegerField(u'порядок следования', blank=True, default=0)

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
    def host_entry(self):
        return self.meaning.host_entry

    def save(self, without_mtime=False, *args, **kwargs):
        super(MeaningContext, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(MeaningContext, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

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

    objects = QuasiGoodManager()
    objects_all = models.Manager()

    class Meta:
        verbose_name = u'контекст значения'
        verbose_name_plural = u'контексты значения'


class Meaning(models.Model):

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

    metaphorical = BooleanField(u'метафорическое', default=False)
    figurative = BooleanField(u'переносное', default=False)
    meaning = TextField(u'значение', blank=True)

    gloss = TextField(u'пояснение', help_text=u'''Для неметафорических
            употреблений/прямых значений здесь указывается энциклопедическая
            информация. Для метафорических/переносных -- (?) разнообразная
            дополнительная информация, комментарии к употреблению.''',
            blank=True)

    substantivus = BooleanField(u'в роли сущ.')
    substantivus_type = CharField(u'форма субстантива', max_length=1,
                                  choices=SUBSTANTIVUS_TYPE_CHOICES,
                                  blank=True, default='')

    def is_substantivus_type(self, slug):
        return SUBSTANTIVUS_TYPE_MAP[slug] == self.substantivus_type

    additional_info = TextField(u'примечание', help_text=u'''Любая
            дополнительная информация по данному ЗНАЧЕНИЮ. Дополнительная
            информация по примеру на значение или лексеме указывается не здесь,
            а в аналогичных полях при примере и лексеме, соответственно.''',
            blank=True)

    @property
    def examples(self):
        return self.example_set.order_by('order', 'id')

    @property
    def contexts(self):
        return self.meaningcontext_set.all()

    @property
    def greek_equivs(self):
        return self.greekequivalentformeaning_set.all().order_by('id')

    @property
    def collogroups(self):
        return self.collocationgroup_set.all().order_by('order', 'id')

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
            return self.collogroup_container.host_entry

    @property
    def host(self):
        if self.entry_container:
            return self.entry_container
        else:
            return self.collogroup_container

    def save(self, without_mtime=False, *args, **kwargs):
        super(Meaning, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Meaning, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

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
        dct['contexts'] = [c.forJSON() for c in self.contexts]
        dct['collogroups'] = [c.forJSON() for c in self.collogroups]
        dct['meanings'] = [m.forJSON() for m in self.child_meanings]
        dct['examples'] = [e.forJSON() for e in self.examples]
        return dct

    class Meta:
        verbose_name = u'значение'
        verbose_name_plural = u'ЗНАЧЕНИЯ'
        ordering = ('id',)


class Example(models.Model):

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

    @property
    def example_ucs(self):
        example = self.example
        first = example[0:1]

        # Особый случай: Начальное заглавное Е при переводе в строчную букву
        # должно становиться широким "е", а не узким.
        if first == u'Е':
                first = u'є'

        return ucs_convert(first.lower() + example[1:])

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
        return self.greekequivalentforexample_set.all().order_by('id')

    audited = BooleanField(u'Пример прошел проверку или взят на проверку',
                           default=False)

    note = TextField(u'комментарий', help_text=u'''Дополнительная
            информация по данному примеру, которая будет видна рядовому
            пользователю словаря''', blank=True)

    additional_info = TextField(u'примечание', help_text=u'''Любая
            дополнительная информация по данному ПРИМЕРУ. Дополнительная
            информация по значению или лексеме указывается не здесь,
            а в аналогичных полях при значении и лексеме, соответственно.''',
            blank=True)

    GREEK_EQ_STATUS = (
        (u'L', u'следует найти'),   # look for
        (u'S', u'не нужны'),        # stop
        (u'C', u'уточнить адрес'),  # check the address
        (u'N', u'найти не удалось'),  # not found
        (u'F', u'найдены'),         # found
        (u'M', u'необходимы для опр-я значения'),  # meaning
        (u'U', u'срочное'),         # urgent
        )

    greek_eq_status = CharField(u'параллели', max_length=1,
            choices=GREEK_EQ_STATUS, default=u'L')
            # 'L' -- статус "следует найти (греч.параллели)"

    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        if self.entry:
            return self.entry
        else:
            return self.meaning.host_entry

    @property
    def host(self):
        if self.collogroup:
            return self.collogroup
        else:
            if self.meaning:
                return self.meaning.host
            else:
                return self.entry

    def save(self, without_mtime=False, *args, **kwargs):
        host_entry = self.host_entry
        self.entry = host_entry
        host = self.host
        if host and 'base_meaning_id' in host.__dict__:
            self.collogroup = host
        super(Example, self).save(*args, **kwargs)
        host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Example, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

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
        return dct

    def __unicode__(self):
        return u'(%s) %s' % (self.address_text, self.example)

    class Meta:
        verbose_name = u'пример'
        verbose_name_plural = u'ПРИМЕРЫ'
        ordering = ('id',)


class CollocationGroup(models.Model):

    base_entry = ForeignKey(Entry, verbose_name=u'лексема',
            help_text=u'''Лексема, при которой будет стоять словосочетание.
            Если есть возможность указать конкретное значение, лучше указать
            вместо лексемы её конкретное значение.''',
            related_name='collocationgroup_set', blank=True, null=True)

    base_meaning = ForeignKey(Meaning, verbose_name=u'значение',
            help_text=u'''Значение, при котором будет стоять словосочетание.''',
            related_name='collocationgroup_set', blank=True, null=True)

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

    order = SmallIntegerField(u'порядок следования', blank=True, default=0)
    ctime = DateTimeField(editable=False, auto_now_add=True)
    mtime = DateTimeField(editable=False, auto_now=True)
    additional_info = TextField(u'примечание', blank=True)

    @property
    def collocations(self):
        return self.collocation_set.all().order_by('order', 'id')

    @property
    def host_entry(self):
        return (self.base_entry or
                self.base_meaning and self.base_meaning.host_entry)

    meanings = property(meanings)
    metaph_meanings = property(metaph_meanings)
    all_meanings = property(all_meanings)
    has_meanings = property(has_meanings)

    def save(self, without_mtime=False, *args, **kwargs):
        super(CollocationGroup, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(CollocationGroup, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

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

    class Meta:
        verbose_name = u'группа словосочетаний'
        verbose_name_plural = u'ГРУППЫ СЛОВОСОЧЕТАНИЙ'
        ordering = ('-id',)


class Collocation(models.Model):

    collogroup = ForeignKey(CollocationGroup,
                            verbose_name=u'группа словосочетаний',
                            related_name='collocation_set')

    collocation = CharField(u'словосочетание', max_length=70)

    @property
    def collocation_ucs(self):
        return ucs_convert(self.collocation)

    civil_equivalent = CharField(u'гражданское написание', max_length=50,
                                 blank=True)
    civil_inverse = CharField(u'гражд. инв.', max_length=50)

    order = SmallIntegerField(u'порядок следования', blank=True, default=0)

    @property
    def etymologies(self):
        etyms = self.etymology_set.filter(language__in=ETYMOLOGY_LANGUAGES)
        etyms = etyms.filter(etymon_to__isnull=True).order_by('order', 'id')
        return etyms

    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        return self.collogroup.host_entry

    def save(self, without_mtime=False, *args, **kwargs):
        self.civil_inverse = self.civil_equivalent[::-1]
        super(Collocation, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Collocation, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

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


class GreekEquivalentForExample(models.Model):

    for_example = ForeignKey(Example)
    unitext = CharField(u'греч. параллель (Unicode)', max_length=100,
                        blank=True)

    mark = CharField(u'грамматическая помета', max_length=20, blank=True)

    source = CharField(u'документальный источник', help_text=u'''Например,
                       Септуагинта или, более узко, разные редакции одного
                       текста.''', max_length=40, blank=True)

    position = PositiveIntegerField(u'позиция в примере', help_text=u'''Номер
                       слова, после которого следует поставить параллель.''',
                       blank=True, null=True)

    initial_form = CharField(u'начальная форма', max_length=100, blank=True)

    note = TextField(u'комментарий', help_text=u'''Любая дополнительная
                     информация по данному греческому эквиваленту, которая
                     будет включена в текст статьи.''',
                     blank=True)

    additional_info = TextField(u'примечание', help_text=u'''Любая
                                дополнительная информация по данному
                                греческому эквиваленту, которая в текст
                                статьи не войдет''', blank=True)

    corrupted = BooleanField(u'текст испорчен', default=False)
    mtime = DateTimeField(editable=False, auto_now=True)
    order = SmallIntegerField(u'порядок следования', blank=True, default=0)

    @property
    def host_entry(self):
        return self.for_example.host_entry

    def save(self, without_mtime=False, *args, **kwargs):
        super(GreekEquivalentForExample, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(GreekEquivalentForExample, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def forJSON(self):
        _fields = (
            'additional_info',
            'corrupted',
            'for_example_id',
            'id',
            'initial_form',
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


class OrthographicVariant(models.Model):

    # словарная статья, к которой относится данный орф. вариант
    entry = ForeignKey(Entry, related_name='orthographic_variants', blank=True,
                       null=True)

    # сам орфографический вариант
    idem = CharField(u'написание', max_length=50)

    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    @property
    def idem_letter_ucs(self):
        return ucs_convert_affix(self.idem.lower())

    order = SmallIntegerField(u'порядок следования', blank=True, default=0)
    no_ref_entry = BooleanField(u'Не делать отсылочной статьи', default=False)
    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        return self.entry

    def save(self, without_mtime=False, *args, **kwargs):
        super(OrthographicVariant, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(OrthographicVariant, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def __unicode__(self):
        return self.idem

    def forJSON(self):
        _fields = (
            'entry_id',
            'id',
            'idem',
            'order',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    class Meta:
        verbose_name = u'вариант'
        verbose_name_plural = u'варианты'
        ordering = ('order', 'id')


class Participle(models.Model):

    # словарная статья, к которой относится данная словоформа
    entry = ForeignKey(Entry, blank=True, null=True)

    PARTICIPLE_CHOICES = PARTICIPLE_CHOICES

    tp = CharField(u'тип причастия', max_length=2, choices=PARTICIPLE_CHOICES)
    idem = CharField(u'словоформа', max_length=50)

    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    order = SmallIntegerField(u'порядок следования', blank=True, default=0)
    mtime = DateTimeField(editable=False, auto_now=True)

    @property
    def host_entry(self):
        return self.entry

    def save(self, without_mtime=False, *args, **kwargs):
        super(Participle, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Participle, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

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


class WordForm(models.Model):
    entry = ForeignKey(Entry, blank=True, null=True)
    idem = CharField(u'словоформа', max_length=50)
    civil_equivalent = CharField(
            u'гражданское написание', max_length=50, blank=True)
    civil_inverse = CharField(u'гражд. инв.', max_length=50, blank=True)
    order = SmallIntegerField(u'порядок следования', blank=True, default=20)
    mtime = DateTimeField(editable=False, auto_now=True)
    reconstructed = BooleanField(u'отсутствует в корпусе', default=False)
    questionable = BooleanField(u'реконструкция ненадёжна', default=False)
    number = CharField(u'число', max_length=1, choices=INFL_NUMBER,
                help_text=u'для сущ., прил., прич. и гл.')
    case = CharField(u'падеж', max_length=1, choices=INFL_CASE,
                help_text=u'для сущ., прил и прич.')
    gender = CharField(u'род', max_length=1, choices=INFL_GENDER,
                help_text=u'для прил. и прич.')
    shortness = CharField(u'краткость', max_length=1, choices=INFL_SHORTNESS,
                help_text=u'для прил. и прич.')
    comparison = CharField(u'степень сравнения', max_length=1,
                choices=INFL_COMPARISON, help_text=u'для прил., прич. и нар.')
    voice = CharField(u'залог', max_length=1, choices=INFL_VOICE,
                help_text=u'для гл. и прич.')
    mood = CharField(u'наклонение', max_length=1, choices=INFL_MOOD,
                help_text=u'только для гл.')
    person = CharField(u'лицо', max_length=1, choices=INFL_PERSON,
                help_text=u'для гл., мест. сущ. и мест. прил.')

    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    @property
    def host_entry(self):
        return self.entry

    def save(self, without_mtime=False, *args, **kwargs):
        self.civil_inverse = self.civil_equivalent[::-1]
        super(WordForm, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(WordForm, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def __unicode__(self):
        return self.civil_equivalent

    def forJSON(self):
        _fields = (
            'case',
            'civil_equivalent',
            'comparison',
            'entry_id',
            'gender',
            'id',
            'idem',
            'mood',
            'number',
            'order',
            'person',
            'questionable',
            'reconstructed',
            'shortness',
            'voice',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    class Meta:
        verbose_name = u'словоформа'
        verbose_name_plural = u'словоформы'
        ordering = ('order', 'id')


class Transcription(models.Model):
    wordform = ForeignKey(WordForm)
    transcription = CharField(
            u'транскрипция', max_length=50, blank=True, default=u'')
    order = SmallIntegerField(u'порядок следования', blank=True, default=0)

    @property
    def host_entry(self):
        return self.wordform.host_entry

    def save(self, without_mtime=False, *args, **kwargs):
        super(Transcription, self).save(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(Transcription, self).delete(*args, **kwargs)
        self.host_entry.save(without_mtime=without_mtime)

    def __unicode__(self):
        return self.transcription

    def forJSON(self):
        _fields = (
            'order',
            'transcription',
            'wordform_id',
        )
        return dict((key, self.__dict__[key]) for key in _fields)


def toJSON(self):
    return json.dumps(self.forJSON(), ensure_ascii=False, separators=(',',':'))

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
    Transcription,
    WordForm,
)
for Model in Models:
    x = get_max_lengths(Model)
    if x:
        MAX_LENGTHS[Model.__name__] = x
    if hasattr(Model, 'forJSON'):
        Model.toJSON = toJSON
