# -*- coding: UTF-8 -*-
from hip2unicode.functions import convert
from hip2unicode.functions import compile_conversion
from hip2unicode.conversions import antconc_ucs8
from hip2unicode.conversions import antconc_ucs8_without_aspiration

compiled_conversion_with_aspiration = compile_conversion(antconc_ucs8.conversion)
compiled_conversion_without_aspiration = compile_conversion(antconc_ucs8_without_aspiration.conversion)

def ucs_convert(text):
    return convert(text, compiled_conversion_with_aspiration).encode('utf-8')

def ucs_convert_affix(text):
    """
    Функции передаётся строка, которая должна содержать строковую запись аффикса
    в свободной форме -- не важно с дефисом или без. Если начальный дефис есть,
    он отбрасывается. Всё оставшееся конвертируется из представления AntConc в UCS8
    без расстановки придыханий перед начальными гласными.
    """
    if text:
        if text[0] == u'-':
            text = text[1:]
        return convert(text, compiled_conversion_without_aspiration).encode('utf-8')
    return text

def ucs_affix_or_word(atr):
    """
    Функция предназначенная для конвертации значения атрибута модели из
    представления AntConc в UCS8. Атрибут должен быть строкой. Если первым
    символом строки является дефис, то сам дефис отбрасывается, а конвертация
    производится без создания придыханий над начальными гласными из
    предположения, что это аффикс. Если первый символ -- не дефис, конвертация
    производится с созданием придыханий, подразумевается, что на вход подано
    слово, а не аффикс.
    """
    if atr:
        if atr[0] == u'-':
            return ucs_convert_affix( atr[1:] )
        else:
            return ucs_convert(atr)
    else:
        return atr

from django.db import models
from custom_user.models import CustomUser
from slavdict.directory.models import (

    PartOfSpeech,
    Gender,
    Tantum,
    Onym,
    Transitivity,
    Language,
    EntryStatus,

    )

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

    lexeme = models.ManyToManyField(
        'Entry',
        verbose_name = u'лексема',
        )

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
        blank = True,
        null = True,
        )

    # orthographic_variants
    @property
    def orth_vars(self):
        return self.orthographic_variants.all()

    @property
    def meanings(self):
        return self.meaning_set.filter(metaphorical=False)

    @property
    def metaph_meanings(self):
        return self.meaning_set.filter(metaphorical=True)

    @property
    def syns(self):
        g = self.synonym_in.all()
        if g:
            g = g[0]
        return g.synonyms.exclude(id=self.id)

    @property
    def base_syn(self):
        g = self.synonym_in.all()
        if g:
            g = g[0]
        return g.base

    @property
    def base_syn_bool(self):
        return self.base_syn.id==self.id

    # lexeme (посредник к граматическим формам и свойствам)

    part_of_speech = models.ForeignKey(
        PartOfSpeech,
        verbose_name = u'часть речи',
        )

    uninflected = models.BooleanField(
        u'неизменяемое (для сущ./прил.)',
        default = False,
        )

    word_forms_list = models.TextField(
        u'список словоформ',
        help_text = u'Список словоформ через запятую',
        blank = True,
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
        max_length = 10,
        blank = True,
        )

    @property
    def genitive_ucs(self):
        return ucs_convert_affix(self.genitive)

    # proper_noun

    # только для прилагательных
    short_form = models.CharField(
        # Это поле, по идее, в последствии должно стать FK
        # или даже MtM с приявязкой к WordForm.
        u'краткая форма',
        max_length = 20,
        blank = True,
        )

    @property
    def short_form_ucs(self):
        return ucs_convert(self.short_form)

    possessive = models.BooleanField(
        u'притяжательное прилагательное',
        default = False,
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
        help_text = u'''Целая словоформа или окончание.
                        В случае окончания первым
                        символом должен идти дефис.''',
        )

    @property
    def sg1_ucs(self):
        return ucs_affix_or_word(self.sg1)

    sg2 = models.CharField(
        u'форма 2sg',
        max_length = 20,
        blank = True,
        help_text = u'''Целая словоформа или окончание.
                        В случае окончания первым
                        символом должен идти дефис.''',
        )

    @property
    def sg2_ucs(self):
        return ucs_affix_or_word(self.sg2)

    derivation_entry = models.ForeignKey(
        'self',
        verbose_name = u'слово, от которого образовано данное слово',
        related_name = 'derived_entries',
        blank = True,
        null = True,
        )

    link_to_entry = models.ForeignKey(
        'self',
        verbose_name = u'ссылка на другую лексему',
        help_text = u'''Если вместо значений словарная статья
                        должна содержать только ссылку
                        на другую словарную статью,
                        укажите её в данном поле.''',
        related_name = 'ref_entries',
        blank = True,
        null = True,
        )

    link_to_phu = models.ForeignKey(
        'PhraseologicalUnit',
        verbose_name = u'ссылка на фразеологическое сочетание',
        help_text = u'''Если вместо значений словарная статья
                        должна содержать только ссылку
                        на фразеологическое сочетание,
                        укажите его в данном поле.''',
        related_name = 'ref_entries',
        blank = True,
        null = True,
        )

    additional_info = models.TextField(
        u'любая дополнительная информация',
        help_text = u'''Любая дополнительная информация по данной ЛЕКСЕМЕ.
                        Дополнительная информация по значению лексемы или
                        примеру на значение указывается не здесь,
                        а в аналогичных полях при значении и примере,
                        соответственно.''',
        blank = True,
        )

    @property
    def etymologies(self):
        return self.etymology_set.all()

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
        CustomUser,
        verbose_name = u'редактор статьи',
        blank = True,
        null = True,
        )

    antconc_query = models.TextField(
        u'Запрос для программы AntConc',
        blank = True,
        )

    grequiv_status = models.CharField(
        u'греческие параллели',
        max_length = 1,
        choices = (
                ('1', u'следует найти параллели'),
                ('2', u'параллели не нужны'),
                ('3', u'идет поиск параллелей'),
                ('4', u'параллели найдены'),
                ('5', u'параллели найдены частично'),
            ),
        blank = True,
        null = True,
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
    is_headword = models.BooleanField(
        u'основной орфографический вариант',
        default = True,
        )

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

    entry = models.ForeignKey(
        # может MtM
        Entry,
        verbose_name = u'словарная статья',
        help_text = u'''Словарная статья, к которой
                        относится данная этимология.''',
        )

    parent_etymology = models.ForeignKey(
        'self',
        verbose_name = u'родительская этимология',
        help_text = u'''Этимология, для которой данная
                        этимология является этимологией.''',
        blank = True,
        null = True,
        )

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
        blank = True,
        )

    meaning = models.CharField(
        u'перевод',
        max_length = 70,
        blank = True,
        )

    gloss = models.CharField(
        u'пояснение',
        max_length = 70,
        blank = True,
        )

    unclear_etymology = models.BooleanField(
        u'этимология неясна',
        default = False,
        )

    mark = models.CharField(
        u'грамматическая помета',
        max_length = 20,
        blank = True,
        )

    additional_info = models.TextField(
        u'любая дополнительная информация',
        blank = True,
        )

    def __unicode__(self):
        return u'%s %s %s' % (self.language.abbreviation, self.entry, self.translit)

    class Meta:
        verbose_name = u'этимология слова'
        verbose_name_plural = u'этимология слов'
        ordering = ('id',)


class ProperNoun(models.Model):

    entry = models.ForeignKey(Entry)

    onym = models.ForeignKey(
        Onym,
        verbose_name = u'тип имени собственного',
        )

    canonical_name = models.BooleanField(
        u'каноническое',
        )

    def __unicode__(self):
        return u'<Имя собственное %s>' % self.id

    class Meta:
        verbose_name = u'имя собственное'
        verbose_name_plural = u'имена собственные'


class MeaningContext(models.Model):

    meaning = models.ForeignKey(
        'Meaning',
        verbose_name = u'значение',
        )

    left_text = models.CharField(
        u'дополнительный текст слева',
        max_length = 20,
        help_text = u'Здесь указывается текст на русском языке.',
        blank = True,
        # пока непонятно будет ли это поле использоваться, т.к.
        # для правых контекстов плюс слева будет добавляться автоматически.
        )

    context = models.CharField(
        u'текст контекста',
        max_length = 40,
        help_text = u'''Здесь указывается церковнославянский текст.
                        Например, если необходим правый контекст «+ къ кому/чему»,
                        в данное поле добавляется текст «къ».''',
        blank = True,
        )

    @property
    def context_ucs(self):
        return ucs_convert(self.context)

    right_text = models.CharField(
        u'дополнительный текст справа',
        max_length = 20,
        help_text = u'''Здесь указывается текст на русском языке.
                        Например, если необходим правый контекст «+ къ кому/чему»,
                        в данное поле добавляется текст «кому/чему».''',
        blank = True,
        )

    def __unicode__(self):
        SPACE = u' '
        _list = (self.left_text, self.context, self.right_text)
        return SPACE.join(_list)

    class Meta:
        verbose_name = u'контекст значения'
        verbose_name_plural = u'контексты значения'


class Meaning(models.Model, AdminInfo):

    entry_container = models.ForeignKey(
        Entry,
        blank = True,
        null = True,
        verbose_name = u'лексема',
        help_text = u'''Лексема, к которой относится значение.
                        Выберите, только если значение
                        не относится к фразеологизму.''',
        )

    phu_container = models.ForeignKey(
        'PhraseologicalUnit',
        blank = True,
        null = True,
        verbose_name = u'фразеологизм',
        help_text = u'''Фразелогическое сочетание,
                        к которому относится значение.
                        Выберите, только если значение
                        не относится к конкретной лексеме.''',
        )

    parent_meaning = models.ForeignKey(
        'self',
        verbose_name = u'родительское значение',
        related_name = 'child_meanings',
        blank = True,
        null = True,
        )

    hidden = models.BooleanField(
        u'Скрыть значение',
        help_text = u'''Не отображать данное значение
                        при выводе словарной статьи.''',
        default = False,
        )

    link_to_meaning = models.ForeignKey(
        'self',
        verbose_name = u'ссылка на значение',
        help_text = u'''Если значение должно вместо текста
                        содержать только ссылку на другое
                        значение некоторой лексемы или
                        фразеологического сочетания,
                        укажите её в данном поле.''',
        related_name = 'ref_meanings',
        blank = True,
        null = True,
        )

    link_to_entry = models.ForeignKey(
        Entry,
        verbose_name = u'ссылка на лексему',
        help_text = u'''Если вместо значения
                        должна быть только ссылка
                        на другую словарную статью,
                        укажите её в данном поле.''',
        related_name = 'ref_meanings',
        blank = True,
        null = True,
        )

    link_to_phu = models.ForeignKey(
        'PhraseologicalUnit',
        verbose_name = u'ссылка на фразеологическое сочетание',
        help_text = u'''Если вместо значения должна быть только ссылка
                        на целое фразеологическое сочетание, а не его
                        отдельные значения, укажите его в данном поле.''',
        related_name = 'ref_meanings',
        blank = True,
        null = True,
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
        u'пояснение',
        help_text = u'''Для неметафорических употреблений/прямых значений
                        здесь указывается энциклопедическая информация.
                        Для метафорических/переносных -- (?) разнообразная
                        дополнительная информация, коментарии к употреблению.''',
        blank = True,
        )

    additional_info = models.TextField(
        u'любая дополнительная информация',
        help_text = u'''Любая дополнительная информация по данному
                        ЗНАЧЕНИЮ. Дополнительная информация по примеру
                        на значение или лексеме указывается не здесь,
                        а в аналогичных полях при примере и лексеме,
                        соответственно.''',
        blank = True,
        )

    @property
    def examples(self):
        return self.example_set.all()

    @property
    def contexts(self):
        return self.meaningcontext_set.all()

    def __unicode__(self):
        return self.meaning

    class Meta:
        verbose_name = u'значение'
        verbose_name_plural = u'значения'
        ordering = ('entry_container__civil_equivalent__text', 'id')


class Example(models.Model, AdminInfo):

    meaning = models.ForeignKey(Meaning)
    # TODO: это должно быть поле ManyToManyField,
    # а не FK. Соответственно, оно должно
    # иметь название во мн.ч. (meaning*s*)

    hidden = models.BooleanField(
        u'Скрыть пример',
        help_text = u'''Не отображать данный пример
                        при выводе словарной статьи.''',
        default = False,
        )

    example = models.TextField(
        u'пример',
        )

    @property
    def example_ucs(self):
        return ucs_convert(self.example)

    context = models.TextField(
        u'контекст примера',
        help_text = u'Более широкий контекст для примера',
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

    # Временное поле для импорта вордовских статей.
    address_text = models.CharField(
        u'адрес',
        max_length = 300,
        blank = True,
        )

    # greek_equivalent

    additional_info = models.TextField(
        u'любая дополнительная информация',
        help_text = u'''Любая дополнительная информация
                        по данному ПРИМЕРУ. Дополнительная
                        информация по значению или лексеме
                        указывается не здесь, а в аналогичных
                        полях при значении и лексеме,
                        соответственно.''',
        blank = True,
        )

    def __unicode__(self):
        return u'(%s) %s' % (self.address, self.example)

    class Meta:
        verbose_name = u'пример'
        verbose_name_plural = u'примеры'


class PhraseologicalUnit(models.Model):

    text = models.CharField(
        u'фразеологическое сочетание',
        max_length = 50,
        )

    @property
    def text_ucs(self):
        return ucs_convert(self.text)

    entry_constituents = models.ManyToManyField(
        Entry,
        verbose_name = u'словарные статьи',
        help_text = u'''Словарные статьи,
                        при которых необходимо
                        разместить фразеологическую
                        единицу или ссылку
                        на её размещение''',
        )

    base = models.ForeignKey(
        Entry,
        verbose_name = u'базовая словарная статья',
        related_name = 'based_phus'
        )

    link_to_entry = models.ForeignKey(
        Entry,
        verbose_name = u'ссылка на лексему',
        help_text = u'''Если вместо значений фразеологической
                        единицы должна быть только ссылка
                        на словарную статью, укажите её
                        в данном поле.''',
        related_name = 'ref_phus'
        blank = True,
        null = True,
        )

    link_to_phu = models.ForeignKey(
        'self',
        verbose_name = u'ссылка на фразеологическое сочетание',
        help_text = u'''Если вместо значений фразеологической
                        единицы должна быть только ссылка
                        на другое фразеологическое сочетание,
                        укажите её в данном поле.''',
        related_name = 'ref_phus'
        blank = True,
        null = True,
        )

    def __unicode__(self):
        return self.text

    class Meta:
        verbose_name = u'фразеологическое сочетание'
        verbose_name_plural = u'фразеологические сочетания'


class SynonymGroup(models.Model):

    entry_synonyms = models.ManyToManyField(
        Entry,
        verbose_name = u'синонимы',
        related_name = 'synonym_in',
        blank = True,
        null = True,
        )

    @property
    def synonyms(self):
        return self.entry_synonyms.all()

    phu_synonyms = models.ManyToManyField(
        PhraseologicalUnit,
        verbose_name = u'синонимы-фразеологизмы',
        blank = True,
        null = True,
        )

    base = models.ForeignKey(
        Entry,
        verbose_name = u'базовый синоним',
        related_name = 'base_synonym_in'
        )

    def __unicode__(self):
        syn_list = self.entry_synonyms + self.phu_synonyms
        return unicode([syn.base.civil_equivalent.text for syn in syn_list])

    class Meta:
        verbose_name = u'группа синонимов'
        verbose_name_plural = u'группы синонимов'


class Collocation(models.Model):

    entry = models.ForeignKey(Entry)

    idem = models.TextField(
        u'словосочетание',
        )

    def __unicode__(self):
        return self.idem
