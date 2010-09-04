# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User

from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import antconc_ucs8

compiled_conversion = compile_conversion(antconc_ucs8.conversion)

def ucs_convert(text):
    return convert(text, compiled_conversion).encode('utf-8')



from slavdict.directory.models import (

    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    Transitivity,
    SubcatFrame,
    Language,
    EntryStatus,

    )

class MyUser(User):

    def __unicode__(self):
        return u'%s %s' % (
            self.last_name,
            self.first_name,
            )

    class Meta:
        proxy = True
        ordering = ('last_name', 'first_name')

class AdminInfo:

    add_datetime = models.DateTimeField(
        editable = False,
        auto_now_add = True,
        )

    change_datetime = models.DateTimeField(
        editable = False,
        auto_now = True,
        )

class CivilEquivalent(models.Model):

    text = models.CharField(
        u'гражданское написание',
        max_length = 40,
        unique = True,
        )

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = u'эквивалент в гражданском написании'
        verbose_name_plural = u'слова в гражданском написании'


class WordForm(models.Model):

    text = models.CharField(
        u'словоформа',
        max_length = 40,
        unique = True,
        )

    def __unicode__(self):
        return self.text


class Entry(models.Model, AdminInfo):

    civil_equivalent = models.ForeignKey(
        CivilEquivalent,
        verbose_name = u'гражданское написание',
        )

    # orthographic_variants
    @property
    def orth_vars(self):
        return self.orthographic_variants.all()

    @property
    def meanings(self):
        return self.meaning_set.all()

    # lexeme (посредник к граматическим формам и свойствам)
    word_forms = models.ManyToManyField(
        WordForm,
        verbose_name = u'словоформы'
        )

    part_of_speech = models.ForeignKey(
        PartOfSpeech,
        verbose_name = u'часть речи',
        )

    uninflected = models.BooleanField(
        u'неизменяемое (для сущ./прил.)',
        )

    # только для существительных
    tantum = models.ForeignKey(
        Tantum,
        blank = True,
        null = True,
        )

    gender = models.ForeignKey(
        Gender,
        verbose_name = u'грам. род',
        blank = True,
        null = True,
        )

    genitive = models.CharField(
        u'окончание Р.п.',
        max_length = 3,
        help_text = u'само окончание без дефиса в начале',
        blank = True,
        )

    @property
    def genitive_ucs(self):
        return ucs_convert(self.genitive)

    # proper_noun

    # только для прилагательных
    short_form = models.CharField(
        u'краткая форма',
        max_length = 20,
        blank = True,
        )

    possessive_pronoun_to = models.ForeignKey(
        'self',
        verbose_name = u'притяж. прил. к',
        blank = True,
        null = True,
        )

    @property
    def short_form_ucs(self):
        return ucs_convert(self.short_form)

    possessive_prounoun_to = models.ForeignKey(
        'self',
        verbose_name = u'притяж. прилагательное от',
        blank = True,
        null = True,
        )

    # только для глаголов
    transitivity = models.ForeignKey(
        Transitivity,
        verbose_name = u'переходность',
        blank = True,
        null = True,
        )

    sg1 = models.CharField(
        u'форма 1sg',
        max_length = 20,
        blank = True,
        )

    @property
    def sg1_ucs(self):
        return ucs_convert(self.sg1)

    sg2 = models.CharField(
        u'форма 2sg',
        max_length = 20,
        blank = True,
        )

    @property
    def sg2_ucs(self):
        return ucs_convert(self.sg2)

    additional_info = models.TextField(
        u'любая дополнительная информация',
        blank = True,
        )

    # административная информация
    status = models.ForeignKey(
        EntryStatus,
        verbose_name = u'статус статьи',
        default = 0,
        )

    percent_status = models.PositiveSmallIntegerField(
        u'статус готовности статьи в процентах',
        default = 0,
        )

    editor = models.ForeignKey(
        MyUser,
        verbose_name = u'ответственный редактор',
        blank = True,
        null = True,
        )

    antconc_query = models.CharField(
        u'Запрос для программы AntConc',
        max_length = 500,
        )

    def __unicode__(self):
        return self.civil_equivalent.text

    class Meta:
        verbose_name = u'словарная статья'
        verbose_name_plural = u'словарные статьи'
        ordering = ('civil_equivalent__text',)


class OrthographicVariant(models.Model):

    # словарная статья, к которой относиться данный орф. вариант
    entry = models.ForeignKey(
        Entry,
        verbose_name = u'словарная статья',
        related_name = 'orthographic_variants'
        )

    # сам орфографический вариант
    idem = models.CharField(
        u'написание',
        max_length=40,
        )

    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    # является ли данное слово реконструкцией (реконструированно, так как не встретилось в корпусе)
    is_reconstructed = models.BooleanField(u'является реконструкцией')

    # в связке с полем реконструкции (is_reconstructed)
    # показывает, утверждена ли реконструкция или нет
    is_approved = models.BooleanField(u'одобренная реконструкция')

    # является ли данный орфографический вариант основным
    is_headword = models.BooleanField(u'основной орфографический вариант')

    # является ли орф. вариант только общей частью словоформ
    # (напр., "вонм-" для "вонми", "вонмем" и т.п.)
    # на конце автоматически добавляется дефис, заносить в базу без дефиса
    is_factored_out = models.BooleanField(u'общая часть нескольких слов или словоформ')

    # частота встречаемости орфографического варианта
    # ? для факторизантов не важна ?
    frequency = models.PositiveIntegerField(
        u'частота',
        blank = True,
        null  = True,
        )

    def __unicode__(self):
        return self.idem

    class Meta:
        verbose_name = u'орфографический вариант'
        verbose_name_plural = u'орфографические варианты'
        ordering = ('-is_headword', 'idem')

class Etymology(models.Model):

    language = models.ForeignKey(
        Language,
        verbose_name = u'язык',
        )

    text = models.CharField(
        u'языковой эквивалент',
        max_length = 40,
        blank = True,
        )

    translit = models.CharField(
        u'траслит.',
        max_length = 40,
        )

    meaning = models.CharField(
        u'перевод',
        max_length = 70,
        )

    def __unicode__(self):
        return self.translit

    class Meta:
        verbose_name = u'этимология слова'
        verbose_name_plural = u'этимология слов'


class ProperNoun(models.Model):

    entry = models.ForeignKey(Entry)

    onym = models.ForeignKey(
        Onym,
        verbose_name = u'тип имени собственного',
        )

    canonical_name = models.BooleanField(
        u'каноническое',
        )

    unclear_ethymology = models.BooleanField(
        u'этимология неясна',
        )

    etymology = models.ManyToManyField(
        Etymology,
        verbose_name = u'этимология',
        blank = True,
        null = True,
        )

    def __unicode__(self):
        return u'<Имя собственное %s>' % self.id

    class Meta:
        verbose_name = u'имя собственное'
        verbose_name_plural = u'имена собственные'


class Meaning(models.Model, AdminInfo):

    entry = models.ForeignKey(
        Entry,
        blank = True,
        null = True,
        verbose_name = u'лексема',
        help_text = u'Лексема, к которой относится значение. Выберите, только если значение не относится к фразеологизму.',
        )

    phraseological_unit = models.ForeignKey(
        'PhraseologicalUnit',
        blank = True,
        null = True,
        verbose_name = u'фразеологизм',
        help_text = u'Фразелогическое сочетание, к которому относится значение. Выберите, только если значение не относится к конкретной лексеме.',
        )

    order = models.IntegerField(
        u'номер',
        )

    link = models.BooleanField(
        u'значение будет ссылкой на значение другого слова',
        help_text = u'если данный флаг выставлен, содержимое поля «значение» отображаться в словарной статье не будет',
        )

    meaning = models.TextField(
        u'значение',
        blank = True,
        )

    metaphorical = models.BooleanField(
        u'метафорическое',
        )

    # greek_equivalent

    gloss = models.TextField(
        u'толкование',
        blank = True,
        )

    subcat_frames = models.ManyToManyField(
        SubcatFrame,
        verbose_name = u'модель управления',
        blank = True,
        null = True,
        )

    additional_info = models.TextField(
        u'любая дополнительная информация',
        blank = True,
        )

    @property
    def examples(self):
        return self.example_set.all()

    def __unicode__(self):
        return self.meaning

    class Meta:
        verbose_name = u'значение'
        verbose_name_plural = u'значения'
        ordering = ('entry__civil_equivalent__text', 'order')


class Address(models.Model):

    address = models.CharField(
        u'адрес',
        max_length = 15,
        )

    def __unicode__(self):
        return u'(%s)' % self.address

    class Meta:
        verbose_name = u'адрес'
        verbose_name_plural = u'адреса'


class Example(models.Model, AdminInfo):

    example = models.TextField(
        u'пример',
        )

    @property
    def example_ucs(self):
        return ucs_convert(self.example)

    context = models.TextField(
        u'контекст примера',
        help_text = u'более широкий контекст для примера',
        blank = True,
        )

    class SplitContext:
        def __init__(self, left, middle, right, whole):
            self.left = left
            self.example = middle
            self.right = right
            self.whole = whole

        def __unicode__(self):
            return self.whole

    @property
    def context_ucs(self):
        c = self.context
        e = ucs_convert(self.example)
        if c:
            c = ucs_convert(c)
            x, y, z = c.partition(e)
            x = strip(x)
            y = strip(y)
            z = strip(z)
            if y:
                # Разбиение дало положительный результат,
                # в "y" помещён сам пример.
                return SplitContext(x, y, z, c)
        return SplitContext(u'', e, u'', e)

    address = models.ForeignKey(
        Address,
        verbose_name = u'адрес',
        # временно поле сделано необязательным
        blank = True,
        null = True,
        )

    # Временное поле для импорта вордовских статей.
    address_text = models.CharField(
        u'текст адреса',
        max_length = 300,
        help_text = u'''Временное поле для импорта
                        вордовских статей. И заполнения
                        адресов в неунифицированном
                        текстовом виде'''
        )

    hidden = models.BooleanField(
        u'не показывать в словарной статье',
        default = False,
        )

    translation = models.TextField(
        u'перевод',
        blank = True,
        )

    meaning = models.ForeignKey(Meaning)
    # TODO: это должно быть поле ManyToManyField,
    # а не FK. Соответственно, оно должно
    # иметь название во мн.ч. (meaning*s*)

    # greek_equivalent

    def __unicode__(self):

        return u'%s %s' % (self.address, self.example)

    class Meta:

        verbose_name = u'пример'
        verbose_name_plural = u'примеры'

class SynonymGroup(models.Model):

    synonyms = models.ManyToManyField(
        Meaning,
        verbose_name = u'синонимы',
        related_name = 'synonym_groups'
        )

    base = models.ForeignKey(
        Meaning,
        verbose_name = u'базовый синоним',
        related_name = 'base_synonyms'
        )

    def __unicode__(self):
        return self.base.entry.civil_equivalent.text

    class Meta:
        verbose_name = u'группа синонимов'
        verbose_name_plural = u'группы синонимов'

class PhraseologicalUnit(models.Model):

    text = models.CharField(
        u'фразеологическое сочетание',
        max_length = 50,
        )

    @property
    def text_ucs(self):
        return ucs_convert(self.text)

    constituents = models.ManyToManyField(
        Entry,
        verbose_name = u'словарные статьи',
        help_text = u'словарные статьи, при которых необходимо разместить фразеологическую единицу или ссылку на её размещение',
        related_name = 'phraseol_units',
        )

    base = models.ForeignKey(
        Entry,
        verbose_name = u'базовая словарная статья',
        related_name = 'base_to_phraseol_units'
        )

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = u'фразеологическое сочетание'
        verbose_name_plural = u'фразеологические сочетания'
