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

    Если входная строка пустая, то возвращается также пустая строка. Если
    непустая, то возвращается кортеж, где второй элемент -- это
    сконверированная строка, а первый -- булевская константа, указывающая,
    является ли строка аффиксом (True) или словом (False).

    Если данная функция используется в другой функции, то последней можно
    давать название с использованием аббревиатуры wax (Word or AffiX).

    Возможно, впоследствии лучше сделать, чтобы функция возвращала не кортеж, а
    объект. В качестве __unicode__ будет возвращаться сконвертированная строка,
    а информация о том, аффикс или нет, отдельным свойством.
    """
    if atr:
        if atr[0] == u'-':
            return ( True, ucs_convert_affix( atr[1:] ) )
        else:
            return ( False, ucs_convert(atr) )
    else:
        return atr

def arabic2roman(number):
    numerals={  1:u"I", 4:u"IV",
                # 5:u"V", 9:u"IX", 10:u"X", 40:u"XL", 50:u"L",
                # 90:u"XC", 100:u"C", 400:u"CD", 500:u"D", 900:u"CM", 1000:u"M"
              }
    result = u""
    for value, numeral in sorted(numerals.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value
    return result


from django.db import models
from custom_user.models import CustomUser
from slavdict.directory.models import CategoryValue

class AdminInfo:

    add_datetime = models.DateTimeField(
        editable = False,
        auto_now_add = True,
        verbose_name = u'время создания',
        )

    change_datetime = models.DateTimeField(
        editable = False,
        auto_now = True,
        verbose_name = u'время изменения',
        )

class Meaningfull:
    """
    У экземпляров класса должен иметься менеджер запросов
    с названием meaning_set.
    """
    @property
    def meanings(self):
        return self.meaning_set.filter(metaphorical=False).order_by('order', 'id')

    @property
    def metaph_meanings(self):
        return self.meaning_set.filter(metaphorical=True).order_by('order', 'id')

    @property
    def all_meanings(self):
        return self.meaning_set.all().order_by('order', 'id')


class Entry(models.Model, Meaningfull):

    civil_equivalent = models.CharField(
        u'гражданское написание',
        max_length = 40,
        )

    @property
    def orth_vars(self):
        return self.orthographic_variants.all()

    hidden = models.BooleanField(
        u'Скрыть лексему',
        help_text = u'Не отображать лексему в списке словарных статей.',
        default = False,
        editable = False,
        )

    homonym_order = models.SmallIntegerField(
        u'номер омонима',
        help_text = u'''Арабская цифра, например, 1, 2, 3...
                        Поле заполняется только при наличии
                        нескольких омонимов.''',
        blank = True,
        null = True,
        )

    @property
    def homonym_order_roman(self):
        ho = self.homonym_order
        return arabic2roman(ho) if ho else None

    homonym_gloss = models.CharField(
        u'подсказка',
        max_length = 40,
        help_text = u'''Пояснение для различения омонимов, например:
                        «предварять» для ВАРИТИ I или «варить» для ВАРИТИ II.
                        Предполагается использовать только для служебных
                        целей, а не для отображения при словарных статьях.''',
        blank = True,
        )

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
        CategoryValue,
        verbose_name = u'часть речи',
        limit_choices_to = {'category__slug': 'partOfSpeech'},
        related_name = 'entries_of_pos',
        )

    uninflected = models.BooleanField(
        u'неизменяемое (для сущ. и прил.)',
        default = False,
        )

    word_forms_list = models.TextField(
        u'список словоформ',
        help_text = u'Список словоформ через запятую',
        blank = True,
        )

    # только для существительных
    tantum = models.ForeignKey(
        CategoryValue,
        verbose_name = u'число',
        limit_choices_to = {'category__slug': 'tantum'},
        related_name = 'entries_of_tantum',
        blank = True,
        null = True,
        )

    gender = models.ForeignKey(
        CategoryValue,
        verbose_name = u'род',
        limit_choices_to = {'category__slug': 'gender'},
        related_name = 'entries_of_gender',
        blank = True,
        null = True,
        )

    genitive = models.CharField(
        u'окончание Р. падежа',
        max_length = 10,
        blank = True,
        )

    @property
    def genitive_ucs(self):
        return ucs_convert_affix(self.genitive)

    onym = models.ForeignKey(
        CategoryValue,
        limit_choices_to = {'category__slug': 'onym'},
        verbose_name = u'тип имени собственного',
        blank = True,
        null = True,
        )

    canonical_name = models.BooleanField(
        u'каноническое',
        default = False,
        )

    nom_sg = models.CharField(
        u'И.ед.м.',
        help_text = u'''Только для этнонимов
                        (например, в словарной статье АГАРЯНЕ,
                        здесь -- АГАРЯНИН).''',
        max_length = 25,
        blank = True,
        null = True,
        )

    nom_pl = models.CharField(
        u'И.мн.',
        help_text = u'''Только для этнонимов
                        (например, в словарной статье АГАРЯНИН,
                        здесь -- АГАРЯНЕ).''',
        max_length = 25,
        blank = True,
        null = True,
        )

    @property
    def nom_sg_ucs_wax(self):
        return ucs_affix_or_word(self.nom_sg)

    @property
    def nom_pl_ucs_wax(self):
        return ucs_affix_or_word(self.nom_pl)

    # только для прилагательных
    short_form = models.CharField(
        # Это поле, по идее, в последствии должно стать FK
        # или даже MtM с приявязкой к WordForm.
        u'краткая форма',
        help_text = u'''Если Вы указываете не всё слово,
                        а только его часть, предваряйте её дефисом.''',
        max_length = 20,
        blank = True,
        )

    @property
    def short_form_ucs_wax(self):
        return ucs_affix_or_word(self.short_form)

    possessive = models.BooleanField(
        u'притяжательное',
        default = False,
        help_text = u'Притяжательное прилагательное.',
        )

    # только для глаголов
    transitivity = models.ForeignKey(
        CategoryValue,
        verbose_name = u'переходность',
        limit_choices_to = {'category__slug': 'transitivity'},
        related_name = 'entries_of_transitivity',
        blank = True,
        null = True,
        )

    sg1 = models.CharField(
        u'форма 1 ед.',
        max_length = 20,
        blank = True,
        help_text = u'''Целая словоформа или окончание.
                        В случае окончания первым
                        символом должен идти дефис.''',
        )

    @property
    def sg1_ucs_wax(self):
        return ucs_affix_or_word(self.sg1)

    sg2 = models.CharField(
        u'форма 2 ед.',
        max_length = 20,
        blank = True,
        help_text = u'''Целая словоформа или окончание.
                        В случае окончания первым
                        символом должен идти дефис.''',
        )

    @property
    def sg2_ucs_wax(self):
        return ucs_affix_or_word(self.sg2)

    participle_type = models.ForeignKey(
        CategoryValue,
        verbose_name = u'тип причастия',
        limit_choices_to = {'category__slug': 'participle_type'},
        related_name = 'entries_of_parttype',
        blank = True,
        null = True,
        )

    derivation_entry = models.ForeignKey(
        'self',
        verbose_name = u'образовано от',
        related_name = 'derived_entry_set',
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
        related_name = 'ref_entry_set',
        blank = True,
        null = True,
        )

    link_to_collogroup = models.ForeignKey(
        'CollocationGroup',
        verbose_name = u'ссылка на словосочетание',
        help_text = u'''Если вместо значений словарная статья
                        должна содержать только ссылку
                        на словосочетание,
                        укажите его в данном поле.''',
        related_name = 'ref_entry_set',
        blank = True,
        null = True,
        )

    link_to_meaning = models.ForeignKey(
        'Meaning',
        verbose_name = u'ссылка на значение',
        help_text = u'''Если вместо значений словарная статья должна
                        содержать только ссылку на опредленное значение лексемы
                        или словосочетания, укажите его в данном поле.''',
        related_name = 'ref_entry_set',
        blank = True,
        null = True,
        )

    cf_entries = models.ManyToManyField(
        'self',
        verbose_name = u'ср. (лексемы)',
        related_name = 'cf_entry_set',
        symmetrical = False,
        blank = True,
        null = True,
        )

    cf_collogroups = models.ManyToManyField(
        'CollocationGroup',
        verbose_name = u'ср. (группы слововосочетаний)',
        related_name = 'cf_entry_set',
        blank = True,
        null = True,
        )

    cf_meanings = models.ManyToManyField(
        'Meaning',
        verbose_name = u'ср. (значения)',
        related_name = 'cf_entry_set',
        blank = True,
        null = True,
        )

    @property
    def cfmeanings(self):
        return self.cf_meanings.all()

    @property
    def cfentries(self):
        return self.cf_entries.all()

    @property
    def cfcollogroups(self):
        return self.cf_collogroups.all()

    additional_info = models.TextField(
        u'примечание к статье',
        help_text = u'''Любая дополнительная информация по данной ЛЕКСЕМЕ.
                        Дополнительная информация по значению лексемы или
                        примеру на значение указывается не здесь,
                        а в аналогичных полях при значении и примере,
                        соответственно.''',
        blank = True,
        )

    @property
    def etymologies(self):
        return self.etymology_set.filter(etymon_to__isnull=True).order_by('order', 'id')

    @property
    def collogroups(self):
        return self.collocationgroup_set.all().order_by('id')

    # административная информация
    status = models.ForeignKey(
        CategoryValue,
        verbose_name = u'статус статьи',
        limit_choices_to = {'category__slug': 'entryStatus'},
        related_name = 'entries_of_status',
        default = 0,
        )

    percent_status = models.PositiveSmallIntegerField(
        u'статус готовности статьи в процентах',
        default = 0,
        )

    editor = models.ForeignKey(
        CustomUser,
        verbose_name = u'автор статьи',
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

    @models.permalink
    def get_absolute_url(self):
        return ('single_entry_url', [str(self.id)])

    def __unicode__(self):
        return self.orth_vars[0].idem

    class Meta:
        verbose_name = u'словарная статья'
        verbose_name_plural = u'СЛОВАРНЫЕ СТАТЬИ'
        ordering = ('-id',)


class Etymology(models.Model):

    entry = models.ForeignKey(
        # может MtM
        Entry,
        verbose_name = u'словарная статья',
        help_text = u'''Словарная статья, к которой
                        относится данная этимология.''',
        blank = True,
        null = True,
        )

    collocation = models.ForeignKey(
        'Collocation',
        verbose_name = u'словосочетание',
        help_text = u'''Словосочетание, к которому
                        относится данная этимология.''',
        blank = True,
        null = True,
        )

    order = models.SmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    etymon_to = models.ForeignKey(
        'self',
        verbose_name = u'этимон для',
        help_text = u'Возможный/несомненный этимон для другого этимона, который и необходимо указать.',
        related_name = 'etymon_set',
        blank = True,
        null = True,
        )

    @property
    def etymons(self):
        return self.etymon_set.filter(etymon_to=self.id).order_by('order', 'id')

    language = models.ForeignKey(
        CategoryValue,
        limit_choices_to = {'category__slug': 'language'},
        verbose_name = u'язык',
        )

    text = models.CharField(
        u'языковой эквивалент',
        max_length = 40,
        blank = True,
        )

    translit = models.CharField(
        u'траслитерация',
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

    source = models.CharField(
        u'документальный источник',
        help_text = u'например, Септуагинта',
        max_length = 40,
        blank = True,
        )

    unclear = models.BooleanField(
        u'этимология неясна',
        default = False,
        )

    questionable = models.BooleanField(
        u'этимология спорна',
        default = False,
        )

    mark = models.CharField(
        u'грамматическая помета',
        max_length = 20,
        blank = True,
        )

    additional_info = models.TextField(
        u'примечание',
        blank = True,
        )

    def __unicode__(self):
        return u'%s %s %s' % (self.language.tag, self.entry, self.translit)

    class Meta:
        verbose_name = u'этимон'
        verbose_name_plural = u'этимология'
        ordering = ('id',)


class MeaningContext(models.Model):

    meaning = models.ForeignKey(
        'Meaning',
        verbose_name = u'значение',
        )

    order = models.SmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    left_text = models.CharField(
        u'дополнительный текст слева',
        max_length = 20,
        help_text = u'''Здесь указывается текст на <span class="green">русском</span> языке.
                        Например, если необходим контекст «<span class="civil">+</span
                        >&nbsp;<span class="cslav">къ</span>&nbsp;<span class="civil">кому/чему</span>»,
                        в данное поле добавляется текст&nbsp;«<span class="typing">+</span>».''',
        blank = True,
        # пока непонятно будет ли это поле использоваться, т.к.
        # для правых контекстов плюс слева будет добавляться автоматически.
        )

    context = models.CharField(
        u'текст контекста',
        max_length = 40,
        help_text = u'''Здесь указывается <span class="green">церковнославянский</span> текст.
                        Например, если необходим контекст «<span class="civil">+</span
                        >&nbsp;<span class="cslav">къ</span>&nbsp;<span class="civil">кому/чему</span>»,
                        в данное поле добавляется текст&nbsp;«<span class="typing">къ</span>».''',
        blank = True,
        )

    @property
    def context_ucs(self):
        return ucs_convert(self.context)

    right_text = models.CharField(
        u'дополнительный текст справа',
        max_length = 20,
        help_text = u'''Здесь указывается текст на <span class="green">русском</span> языке.
                        Например, если необходим контекст «<span class="civil">+</span
                        >&nbsp;<span class="cslav">къ</span>&nbsp;<span class="civil">кому/чему</span>»,
                        в данное поле добавляется текст&nbsp;«<span class="typing">кому/чему</span>».''',
        blank = True,
        )

    def __unicode__(self):
        SPACE = u' '
        _list = (self.left_text, self.context, self.right_text)
        return SPACE.join(_list)

    class Meta:
        verbose_name = u'контекст значения'
        verbose_name_plural = u'контексты значения'


class Meaning(models.Model):

    entry_container = models.ForeignKey(
        Entry,
        blank = True,
        null = True,
        verbose_name = u'лексема',
        help_text = u'''Лексема, к которой относится значение.
                        Выберите, только если значение
                        не относится к словосочетанию.''',
        related_name = 'meaning_set',
        )

    collogroup_container = models.ForeignKey(
        'CollocationGroup',
        blank = True,
        null = True,
        verbose_name = u'словосочетание',
        help_text = u'''Словосочетание,
                        к которому относится значение.
                        Выберите, только если значение
                        не относится к конкретной лексеме.''',
        related_name = 'meaning_set',
        )

    order = models.SmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    parent_meaning = models.ForeignKey(
        'self',
        verbose_name = u'родительское значение',
        related_name = 'child_meaning_set',
        blank = True,
        null = True,
        )

    hidden = models.BooleanField(
        u'Скрыть значение',
        help_text = u'''Не отображать данное значение
                        при выводе словарной статьи.''',
        default = False,
        editable = False,
        )

    link_to_meaning = models.ForeignKey(
        'self',
        verbose_name = u'ссылка на значение',
        help_text = u'''Если значение должно вместо текста
                        содержать только ссылку на другое
                        значение некоторой лексемы или
                        словосочетания,
                        укажите её в данном поле.''',
        related_name = 'ref_meaning_set',
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
        related_name = 'ref_meaning_set',
        blank = True,
        null = True,
        )

    link_to_collogroup = models.ForeignKey(
        'CollocationGroup',
        verbose_name = u'ссылка на словосочетание',
        help_text = u'''Если вместо значения должна быть только ссылка
                        на целое словосочетание.''',
        related_name = 'ref_meaning_set',
        blank = True,
        null = True,
        )

    cf_entries = models.ManyToManyField(
        Entry,
        verbose_name = u'ср. (лексемы)',
        related_name = 'cf_meaning_set',
        blank = True,
        null = True,
        )

    cf_collogroups = models.ManyToManyField(
        'CollocationGroup',
        verbose_name = u'ср. (группы слововосочетаний)',
        related_name = 'cf_meaning_set',
        blank = True,
        null = True,
        )

    cf_meanings = models.ManyToManyField(
        'self',
        verbose_name = u'ср. (значения)',
        related_name = 'cf_meaning_set',
        symmetrical = False,
        blank = True,
        null = True,
        )

    @property
    def cfmeanings(self):
        return self.cf_meanings.all()

    @property
    def cfentries(self):
        return self.cf_entries.all()

    @property
    def cfcollogroups(self):
        return self.cf_collogroups.all()

    metaphorical = models.BooleanField(
        u'метафорическое',
        default = False,
        )

    meaning = models.TextField(
        u'значение',
        blank = True,
        )

    gloss = models.TextField(
        u'пояснение',
        help_text = u'''Для неметафорических употреблений/прямых значений
                        здесь указывается энциклопедическая информация.
                        Для метафорических/переносных -- (?) разнообразная
                        дополнительная информация, комментарии к употреблению.''',
        blank = True,
        )

    substantivus = models.BooleanField(u'в роли сущ.')

    substantivus_type = models.ForeignKey(
        CategoryValue,
        limit_choices_to = {'category__slug': 'substantivus'},
        verbose_name = u'форма субстантива',
        blank = True,
        null = True,
        )

    additional_info = models.TextField(
        u'примечание',
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

    @property
    def greek_equivs(self):
        return self.greekequivalentformeaning_set.all().order_by('id')

    @property
    def collogroups(self):
        return self.collocationgroup_set.all().order_by('id')

    def __unicode__(self):
        return self.meaning

    class Meta:
        verbose_name = u'значение'
        verbose_name_plural = u'ЗНАЧЕНИЯ'
        ordering = ('id',)


class Example(models.Model):

    meaning = models.ForeignKey(
        Meaning,
        verbose_name = u'значение',
        help_text = u'Значение, к которому относится данный пример.',
        )
    # TODO: это должно быть поле ManyToManyField,
    # а не FK. Соответственно, оно должно
    # иметь название во мн.ч. (meaning*s*)

    order = models.SmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    hidden = models.BooleanField(
        u'Скрыть пример',
        help_text = u'''Не отображать данный пример
                        при выводе словарной статьи.''',
        default = False,
        editable = False,
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
        editable = False,
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

    # Времеis_headwordнное поле для импорта вордовских статей.
    address_text = models.CharField(
        u'адрес',
        max_length = 300,
        blank = True,
        )

    @property
    def greek_equivs(self):
        return self.greekequivalentforexample_set.all().order_by('id')

    additional_info = models.TextField(
        u'примечание',
        help_text = u'''Любая дополнительная информация
                        по данному ПРИМЕРУ. Дополнительная
                        информация по значению или лексеме
                        указывается не здесь, а в аналогичных
                        полях при значении и лексеме,
                        соответственно.''',
        blank = True,
        )

    GREEK_EQ_STATUS = (
        (u'L', u'следует найти'),   # look for
        (u'S', u'не нужны'),        # stop
        (u'A', u'проверить'),       # audit
        (u'C', u'уточнить адрес'),  # check the address
        (u'N', u'найти не удалось'),# not found
        (u'F', u'найдены'),         # found
        )

    greek_eq_status = models.CharField(
        u'параллели',
        max_length = 1,
        choices = GREEK_EQ_STATUS,
        default = u'L', # следует найти
        )

    def __unicode__(self):
        return u'(%s) %s' % (self.address_text, self.example)

    class Meta:
        verbose_name = u'пример'
        verbose_name_plural = u'ПРИМЕРЫ'
        ordering = ('id',)


class CollocationGroup(models.Model, Meaningfull):

    base_entry = models.ForeignKey(
        Entry,
        verbose_name = u'лексема',
        help_text = u'''Лексема, при которой будет стоять
                        словосочетание. Если есть возможность указать
                        конкретное значение, лучше указать вместо лексемы
                        её конкретное значение.''',
        related_name = 'collocationgroup_set',
        blank = True,
        null = True,
        )

    base_meaning = models.ForeignKey(
        Meaning,
        verbose_name = u'значение',
        help_text = u'''Значение, при котором будет стоять
                        словосочетание.''',
        related_name = 'collocationgroup_set',
        blank = True,
        null = True,
        )

    link_to_entry = models.ForeignKey(
        Entry,
        verbose_name = u'ссылка на лексему',
        help_text = u'''Если вместо значений словосочетания
                        должна быть только ссылка
                        на словарную статью, укажите её
                        в данном поле.''',
        related_name = 'ref_collogroup_set',
        blank = True,
        null = True,
        )

    link_to_meaning = models.ForeignKey(
        'Meaning',
        verbose_name = u'ссылка на значение',
        help_text = u'''Если вместо значений словосочетания должна быть
                        только ссылка на опредленное значение лексемы
                        или словосочетания, укажите его в данном поле.''',
        related_name = 'ref_collogroup_set',
        blank = True,
        null = True,
        )

    cf_entries = models.ManyToManyField(
        Entry,
        verbose_name = u'ср. (лексемы)',
        related_name = 'cf_collogroup_set',
        blank = True,
        null = True,
        )

    cf_meanings = models.ManyToManyField(
        Meaning,
        verbose_name = u'ср. (значения)',
        related_name = 'cf_collogroup_set',
        blank = True,
        null = True,
        )

    @property
    def collocations(self):
        return self.collocation_set.all().order_by('order', 'id')

    class Meta:
        verbose_name = u'группа словосочетаний'
        verbose_name_plural = u'ГРУППЫ СЛОВОСОЧЕТАНИЙ'
        ordering = ('-id',)


class Collocation(models.Model):

    collogroup = models.ForeignKey(
        CollocationGroup,
        verbose_name = u'группа словосочетаний',
        )

    collocation = models.CharField(
        u'словосочетание',
        max_length = 70,
        )

    @property
    def collocation_ucs(self):
        return ucs_convert(self.collocation)

    civil_equivalent = models.CharField(
        u'гражданское написание',
        max_length = 40,
        blank = True,
        )

    order = models.SmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    @property
    def etymologies(self):
        return self.etymology_set.filter(etymon_to__isnull=True).order_by('order', 'id')

    def __unicode__(self):
        return self.collocation

    class Meta:
        verbose_name = u'словосочетание'
        verbose_name_plural = u'ОТДЕЛЬНЫЕ СЛОВОСОЧЕТАНИЯ'
        ordering = ('id',)




class GreekEquivalent(models.Model):

    class Meta:
        abstract = True

    text = models.CharField(
        u'греч. параллель',
        max_length = 100,
        )

    mark = models.CharField(
        u'грамматическая помета',
        max_length = 20,
        blank = True,
        )

    source = models.CharField(
        u'документальный источник',
        help_text = u'''Например, Септуагинта или,
                        более узко, разные редакции
                        одного текста.''',
        max_length = 40,
        blank = True,
        )

    additional_info = models.TextField(
        u'примечание',
        help_text = u'Любая дополнительная информация ' \
                    u'по данному греческому эквиваленту.',
        blank = True,
        )

    def __unicode__(self):
        return self.text


class GreekEquivalentForMeaning(GreekEquivalent):

    for_meaning = models.ForeignKey(Meaning)

    class Meta:
        verbose_name = u'греческая параллель для значения'
        verbose_name_plural = u'греческие параллели'


class GreekEquivalentForExample(GreekEquivalent):

    for_example = models.ForeignKey(Example)

    position = models.PositiveIntegerField(
        verbose_name = u'позиция в примере',
        help_text = u'Номер слова, после которого следует поставить параллель.',
        blank = True,
        null = True,
        )

    class Meta:
        verbose_name = u'греческая параллель для примера'
        verbose_name_plural = u'греческие параллели'






class OrthographicVariant(models.Model):

    # словарная статья, к которой относится данный орф. вариант
    entry = models.ForeignKey(
        Entry,
        related_name = 'orthographic_variants',
        blank = True,
        null = True,
        )

    # сам орфографический вариант
    idem = models.CharField(
        u'написание',
        max_length = 50,
        )

    @property
    def idem_ucs(self):
        return ucs_convert(self.idem)

    order = models.SmallIntegerField(
        u'порядок следования',
        blank = True,
        null = True,
        )

    # является ли данное слово реконструкцией (реконструированно, так как не встретилось в корпусе)
    is_reconstructed = models.BooleanField(
        u'является реконструкцией',
        default = False,
        )

    # в связке с полем реконструкции (is_reconstructed)
    # показывает, утверждена ли реконструкция или нет
    is_approved = models.BooleanField(
        u'одобренная реконструкция',
        default = False,
        )

    # является ли орф. вариант только общей частью словоформ
    # (напр., "вонм-" для "вонми", "вонмем" и т.п.)
    # на конце автоматически добавляется дефис, заносить в базу без дефиса
    #is_factored_out = models.BooleanField(u'общая часть нескольких слов или словоформ')

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
        ordering = ('order','id')






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

    collogroup_synonyms = models.ManyToManyField(
        CollocationGroup,
        verbose_name = u'синонимы-словосочетания',
        blank = True,
        null = True,
        )

    base = models.ForeignKey(
        Entry,
        verbose_name = u'базовый синоним',
        related_name = 'base_synonym_in'
        )

    def __unicode__(self):
        _output = [syn.orth_vars[0] for syn in self.entry_synonyms]
        _collocations = [syn.collocation for syn in [collogroup.collocations for collogroup in self.collogroup_synonyms]]
        return _output.extend(_collocations)

    class Meta:
        verbose_name = u'группа синонимов'
        verbose_name_plural = u'группы синонимов'
