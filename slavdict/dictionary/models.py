import datetime
import json
import logging
import re
import unicodedata

from collections import Counter, defaultdict
from collections.abc import Sequence

import markdown

from django.db import models
from django.db import transaction
from django.db.models import BooleanField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import SmallIntegerField
from django.db.models import TextField
from django.db.utils import OperationalError
from django.db.utils import ProgrammingError
from django.urls import reverse
from django.utils.safestring import mark_safe

from slavdict.custom_user.models import CustomUser
from slavdict.dictionary import constants
from slavdict.dictionary.special_cases import special_cases_func
from slavdict.dictionary.utils import antconc_anticorrupt
from slavdict.dictionary.utils import apply_to_mixed
from slavdict.dictionary.utils import arabic2roman
from slavdict.dictionary.utils import CIVIL_IN_CSL_APPLY_TO_CSL
from slavdict.dictionary.utils import civilrus_convert
from slavdict.dictionary.utils import collogroup_sort_key
from slavdict.dictionary.utils import several_wordforms
from slavdict.dictionary.utils import ucs_affix_or_word
from slavdict.dictionary.utils import ucs_convert as ucs8
from slavdict.dictionary.utils import ucs_convert_affix

from crum import get_current_user


logger = logging.getLogger('slavdict')


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


class WithoutHiddenManager(models.Manager):
    def get_queryset(self):
        return super(WithoutHiddenManager,
                     self).get_queryset().filter(hidden=False)


class JSONSerializable:

    def forJSON(self):
        raise NotImplementedError

    def toJSON(self):
        return json.dumps(self.forJSON(),
                          ensure_ascii=False, separators=(',', ':'))

class VolumeAttributive:

    def is_in_volume(self, volume=constants.YET_NOT_IN_VOLUMES):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.is_in_volume(volume)
        return False


class MockOrthographicVariant:
    def __getattribute__(self, attrname):
        return lambda *args, **kwargs: None


class Entry(models.Model, JSONSerializable):

    civil_equivalent = CharField('гражд. написание', max_length=50)
    civil_inverse = CharField('гражд. инв.', max_length=50)
    mock = [MockOrthographicVariant()]

    @property
    def orth_vars(self):
        return self.orthographic_variants.all() or mock

    @property
    def orth_vars_refs(self):
        return self.orthographic_variants.filter(no_ref_entry=False) or mock

    @property
    def base_vars(self):
        return self.orthographic_variants.filter(parent__isnull=True) or mock

    hidden = BooleanField('Скрыть лексему', help_text='''Не отображать лексему
            в списке словарных статей.''', default=False, editable=False)

    homonym_order = SmallIntegerField('номер омонима', help_text='''Арабская
            цифра, например, 1, 2, 3... Поле заполняется только при наличии
            нескольких омонимов.''', blank=True, null=True)

    homonym_gloss = CharField('подсказка', max_length=40, help_text='''
            Пояснение для различения омонимов, например: «предварять» для
            ВАРИТИ I или «варить» для ВАРИТИ II. Предполагается использовать
            только для служебных целей, а не для отображения при словарных
            статьях.''', blank=True)

    duplicate = BooleanField('дубликат', help_text='''В нормальном случае
            дубликатов словарных статей быть не должно. Они возникают только
            в результате недосмотра при создании новый статей вручную или в
            результате недостаточно хороших проверок при автоматизированном
            импорте заготовок статей.''', default=False)

    part_of_speech = CharField('часть речи', max_length=1,
            choices=constants.BLANK_CHOICE + constants.PART_OF_SPEECH_CHOICES,
            default='', blank=True)

    def is_part_of_speech(self, *slugs):
        for slug in slugs:
            if constants.PART_OF_SPEECH_MAP[slug] == self.part_of_speech:
                return True

    restricted_use = BooleanField('слово с ограниченной сочетаемостью',
            default=False)

    # Для сущ. и прил.
    uninflected = BooleanField('неизменяемое', default=False)

    word_forms_list = TextField('список словоформ', help_text='''Список
            словоформ через запятую''', blank=True)

    # только для существительных
    tantum = CharField('число', choices=constants.TANTUM_CHOICES,
                       max_length=1, blank=True, default='')

    def is_tantum(self, slug):
        return constants.TANTUM_MAP[slug] == self.tantum

    gender = CharField('род', choices=constants.GENDER_CHOICES,
                       max_length=1, blank=True, default='')

    def is_gender(self, slug):
        return constants.GENDER_MAP[slug] == self.gender

    genitive = CharField('форма Р. падежа', max_length=50, blank=True)

    @property
    def genitive_ucs_wax(self):
        return ucs_affix_or_word(self.genitive)

    @property
    def genitives(self):
        return several_wordforms(self.genitive)

    onym = CharField('тип имени собственного', max_length=1, blank=True,
                     choices=constants.ONYM_CHOICES, default='')

    def is_onym(self, slug):
        return constants.ONYM_MAP[slug] == self.onym

    canonical_name = BooleanField('каноническое', default=False)

    nom_pl = CharField('И.мн.', help_text='''Только для этнонимов
                       (например, в словарной статье АГАРЯНИН, здесь --
                       АГАРЯНЕ).''', max_length=50, blank=True, default='')

    @property
    def nom_pl_ucs_wax(self):
        return ucs_affix_or_word(self.nom_pl)

    @property
    def ethnonyms(self):
        return several_wordforms(self.nom_pl)

    # только для прилагательных
    short_form = CharField('краткая форма', help_text='''Если Вы указываете
                           не всё слово, а только его часть, предваряйте её
                           дефисом.''', max_length=50, blank=True)

    @property
    def short_form_ucs_wax(self):
        return ucs_affix_or_word(self.short_form)

    @property
    def short_forms(self):
        return several_wordforms(self.short_form)

    possessive = BooleanField('притяжательное', default=False,
                              help_text='Притяжательное прилагательное.')

    comparative = BooleanField('сравн. степ.', default=False,
            help_text='Сравнительная степень прилагательного или наречия')

    # только для глаголов
    transitivity = CharField('переходность', max_length=1, blank=True,
                             choices=constants.TRANSITIVITY_CHOICES, default='')

    def is_transitivity(self, slug):
        return constants.TRANSITIVITY_MAP[slug] == self.transitivity

    @property
    def transitivity_from_meanings(self):
        labile = constants.TRANSITIVITY_MAP['labile']
        trans = constants.TRANSITIVITY_MAP['transitive']
        intrans = constants.TRANSITIVITY_MAP['intransitive']
        tmap = dict(constants.TRANSITIVITY_CHOICES)
        lst = [_f for _f in (m.transitivity for m in self.meanings) if _f]
        template = '%s и\u00a0%s'
        if len(lst) == 0:
            return ''
        elif len(set(lst)) == 1 and \
                not (lst[0] == labile and self.special_case == constants.SC9):
            return tmap.get(lst[0], '')
        else:
            c = Counter(lst)
            if labile in c:
                c[trans] += c[labile]
                c[intrans] += c[labile]
            if c[trans] < c[intrans] or \
                    c[trans] >= c[intrans] and \
                    self.special_case == constants.SC9:
                return template % (tmap[intrans], tmap[trans])
            else:
                return template % (tmap[trans], tmap[intrans])

    sg1 = CharField('форма 1 ед.', max_length=50, blank=True,
                    help_text='''Целая словоформа или окончание. В случае
                    окончания первым символом должен идти дефис.''')

    @property
    def sg1_ucs_wax(self):
        return ucs_affix_or_word(self.sg1)

    @property
    def several_sg1(self):
        return several_wordforms(self.sg1)

    sg2 = CharField('форма 2 ед.', max_length=50, blank=True,
                    help_text='''Целая словоформа или окончание. В случае
                    окончания первым символом должен идти дефис.''')

    @property
    def sg2_ucs_wax(self):
        return ucs_affix_or_word(self.sg2)

    @property
    def several_sg2(self):
        return several_wordforms(self.sg2)

    participle_type = CharField('тип причастия', max_length=1, blank=True,
                    choices=constants.PARTICIPLE_TYPE_CHOICES, default='')

    def is_participle_type(self, slug):
        return constants.PARTICIPLE_TYPE_MAP[slug] == self.participle_type

    derivation_entry = ForeignKey('self', verbose_name='образовано от',
            related_name='derived_entry_set', blank=True, null=True,
            on_delete=models.SET_NULL)

    link_to_entry = ForeignKey('self', verbose_name='ссылка на другую лексему',
            help_text='''Если вместо значений словарная статья должна содержать
            только ссылку на другую словарную статью, укажите её в данном
            поле.''', related_name='ref_entry_set', blank=True, null=True,
            on_delete=models.SET_NULL)

    link_to_collogroup = ForeignKey('CollocationGroup',
            verbose_name='ссылка на словосочетание', help_text='''Если вместо
            значений словарная статья должна содержать только ссылку на
            словосочетание, укажите его в данном поле.''',
            related_name='ref_entry_set', blank=True, null=True,
            on_delete=models.SET_NULL)

    link_to_meaning = ForeignKey('Meaning', verbose_name='ссылка на значение',
            help_text='''Если вместо значений словарная статья должна
            содержать только ссылку на опредленное значение лексемы или
            словосочетания, укажите его в данном поле.''',
            related_name='ref_entry_set', blank=True, null=True,
            on_delete=models.SET_NULL)

    cf_entries = ManyToManyField('self', verbose_name='ср. (лексемы)',
            related_name='cf_entry_set', symmetrical=False, blank=True)

    cf_collogroups = ManyToManyField('CollocationGroup',
            verbose_name='ср. (группы слововосочетаний)',
            related_name='cf_entry_set', blank=True)

    cf_meanings = ManyToManyField('Meaning', verbose_name='ср. (значения)',
            related_name='cf_entry_set', blank=True)

    @property
    def cfmeanings(self):
        return self.cf_meanings.all()

    @property
    def cfentries(self):
        IDEM = (
            r'idem\['
                r'\s*([а-яА-Я]+)'  # Гражданское написание заглавного слова
                r'\s*([1-9])?'  # Номер омонима
                r'(?:\s*-\s*'  # Список значений
                    r'\d+(?:\s*,\s*\d+)*'
                r')?'
            r'\]'
        )
        idems = []
        for m in self.meanings:
            for match in re.findall(IDEM, '%s %s' % (m.meaning, m.gloss)):
                idems.append((match[0], int(match[1]) if match[1] else None))
        cf_entries = self.cf_entries
        for civil_equivalent, homonym_order in idems:
            kwargs = { 'civil_equivalent': civil_equivalent }
            if homonym_order:
                kwargs['homonym_order'] = homonym_order
            cf_entries = cf_entries.exclude(**kwargs)
        return cf_entries.order_by('civil_equivalent')

    @property
    def cfcollogroups(self):
        return self.cf_collogroups.all()

    additional_info = TextField('примечание к статье',
            help_text='''Любая дополнительная информация по данной ЛЕКСЕМЕ.
            Дополнительная информация по значению лексемы или примеру на
            значение указывается не здесь, а в аналогичных полях при значении
            и примере, соответственно.''', blank=True)

    @property
    def etymologies(self):
        etyms = self.etymology_set.filter(
                    language__in=constants.ETYMOLOGY_LANGUAGES)
        etyms = list(etyms)
        etyms.sort(key=lambda x: (bool(x.etymon_to), x.order, x.id))
        return etyms

    @property
    def collogroups(self):
        return self.collocationgroup_set.all().order_by('order', 'id')

    @property
    def participles(self):
        return self.participle_set.all().order_by('order', 'id')

    # административная информация
    status = CharField('статус статьи', max_length=1,
                       choices=constants.STATUS_CHOICES,
                       default=constants.DEFAULT_ENTRY_STATUS)

    def is_status(self, slug):
        return constants.STATUS_MAP[slug] == self.status

    authors = ManyToManyField(CustomUser, verbose_name='автор статьи',
                              blank=True)

    temp_editors = ManyToManyField(CustomUser, related_name='temp_editors_set',
            verbose_name='временные редакторы', blank=True,
            through='TempEdit')
    # When a temporary editor for an entry should be assigned, use the
    # following code:
    #
    #   entry.temp_editors.add(user, through_defaults={
    #       'deadline': date(2020, 03, 15) })

    antconc_query = TextField('запрос для программы AntConc', blank=True)
    mtime = DateTimeField(editable=False)
    ctime = DateTimeField(editable=False, auto_now_add=True)

    LAST_TEMPLATE_VERSION = 2
    template_version = SmallIntegerField('версия структуры статей',
            blank=True, default=LAST_TEMPLATE_VERSION)
    # 0 -- В этих статьях иллюстрации возможны при любых словосочетаниях,
    #      а помета при переводах разрешена только "в Син. пер."
    #      (тома I—III, буквы А—Е);
    # 1 -- Иллюстрации возможны при любых словосочетаниях, но при переводах
    #      разрешен весь спектр помет (предполагается для переиздания
    #      первых трех томов);
    # 2 -- Иллюстрации можно добавлять только к фразеологическим
    #      словосочетаниям и весь спектр помет источников при
    #      переводах (тома, начиная с IV, буквы после Е).

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
                        meaning.index_mark = str(i + 1)
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
                        mgroup.index_mark = arabic2roman(i + 1)
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
            groups = [(key, sorted(value)) for key, value in list(dd.items())]
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

        elif any(m.special_case and m.special_case in constants.POS_SPECIAL_CASES
                 for m in meanings):
            several_pos = True
            ENTRY_POS = self.get_part_of_speech_display()
            pos = meanings[0].special_case
            mm = []
            for m in meanings:
                if m.special_case != pos:
                    pos_mark = constants.POS_SPECIAL_CASES_MAP.get(pos, ENTRY_POS)
                    group = MeaningGroup(mm, pos_mark=pos_mark)
                    meaning_groups.append(group)
                    pos = m.special_case
                    mm = []
                mm.append(m)
            pos_mark = constants.POS_SPECIAL_CASES_MAP.get(pos, ENTRY_POS)
            group = MeaningGroup(mm, pos_mark=pos_mark)
            meaning_groups.append(group)
        else:
            meaning_groups = [MeaningGroup(meanings)]
        return MeaningGroups(meaning_groups, several_pos)

    special_cases = special_cases_func
    special_case = CharField('Статья нуждается в специальной обработке',
            max_length=1, choices=constants.ENTRY_SPECIAL_CASES_CHOICES,
            default='', blank=True)

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
        self._examples = []
        for mgroup in self.meaning_groups:
            for meaning in mgroup.meanings:
                examples = []
                if meaning.examples:
                    examples.extend(meaning.examples)
                for submeaning in meaning.child_meanings:
                    examples.extend(submeaning.examples)
                exgroups.append(ExamplesGroup(examples, mgroup, meaning))
                self._examples.extend(examples)
                collogroups = \
                        meaning.collogroups_non_phraseological + \
                        meaning.collogroups_phraseological
                for cg in collogroups:
                    cg_meanings = tuple(cg.meanings)
                    cg_metaph_meanings = tuple(cg.metaph_meanings)
                    meanings = cg_meanings + cg_metaph_meanings
                    for meaning in meanings:
                        meaning_examples = list(meaning.examples)
                        for submeaning in meaning.child_meanings:
                            meaning_examples.extend(submeaning.examples)
                        exgroup = ExamplesGroup(meaning_examples,
                                                mgroup, meaning, cg)
                        self._examples.extend(meaning_examples)
                        exgroups.append(exgroup)
        self._exgroups = exgroups
        return exgroups

    def all_examples(self):
        if not hasattr(self, '_examples'):
            self.examples_groups_for_hellinists()
        return self._examples

    def get_all_greeks(self):
        greeks = set()
        greeks.update(
            unicodedata.normalize('NFC', et.unitext.strip().lower())
            for et in self.etymology_set.filter(
                            language=constants.LANGUAGE_MAP['greek'])
            if et.unitext.strip() and ' ' not in et.unitext.strip())
        for ex in self.all_examples():
            for ge in ex.greek_equivs:
                text = ge.initial_form.strip().lower()
                if text and not ge.aliud and not re.findall(r'[\sa-zA-Z]', text):
                    text = unicodedata.normalize('NFC', text)
                    greeks.add(text)
        return tuple(sorted(greeks))

    def get_search_item(self):
        NON_POS = (constants.PART_OF_SPEECH_MAP['letter'],
                   constants.PART_OF_SPEECH_MAP['number'])
        HAS_POS = self.part_of_speech and self.part_of_speech not in NON_POS
        pos = ''
        if self.homonym_order and HAS_POS:
            pos = self.get_part_of_speech_display()
        return {
            'id': self.id,
            'civil': self.civil_equivalent,
            'headword': self.orth_vars[0].idem_ucs,
            'hom': self.homonym_order,
            'pos': pos,
            'hint': self.homonym_gloss,
            'url': self.get_absolute_url(),
        }

    @property
    def has_collogroups(self):
        meaning_collogroups = any(m.collogroups.count() for m in self.all_meanings)
        return meaning_collogroups or self.collogroups.count()

    @property
    def has_mforms(self):
        if any(m.substantivus_csl.strip() for m in self.meaning_set.all()):
            return True
        if any(m.substantivus_csl.strip()
               for mm in self.meanings
                   for cg in mm.collogroups
                       for m in cg.meanings):
            return True
        if any(m.substantivus_csl.strip()
               for cg in self.collogroups
                   for m in cg.meanings):
            return True
        return False

    @property
    def has_mcsl(self):
        if any(m.has_mcsl for m in self.meaning_set.all()):
            return True
        if any(m.has_mcsl
               for mm in self.meanings
                   for cg in mm.collogroups
                       for m in cg.meanings):
            return True
        if any(m.has_mcsl
               for cg in self.collogroups
                   for m in cg.meanings):
            return True
        return False

    # Залочена статья для редактирования,
    # во время подготовки тома к печати или нет.
    @property
    def preplock(self):
        yet_not_in_volumes = self.volume == constants.YET_NOT_IN_VOLUMES
        not_in_locked_letters = self.first_letter() not in constants.LOCKED_LETTERS
        if yet_not_in_volumes or not_in_locked_letters:
            return False
        return True

    def first_letter(self):
        return self.civil_equivalent.lstrip(' =*')[:1].lower()

    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
                    blank=True, default=constants.DEFAULT_VOLUME_CHOICE)
    tmp_volume = SmallIntegerField('предыдущее значение поля «Том»',
                    blank=True, null=True)

    @property
    def volume_in_roman(self):
        if self.volume > 0:
            return arabic2roman(self.volume)
        return '*'

    def is_in_volume(self, volume=constants.YET_NOT_IN_VOLUMES):
        if volume is constants.WHOLE_DICTIONARY:
            return self.volume > 0
        first_letter = self.first_letter()

        # Если аргумент volume не передан, то выбираем только те статьи,
        # для которых том ещё не определен.
        if volume is constants.YET_NOT_IN_VOLUMES:
            return self.volume == 0
        else:
            if isinstance(volume, (list, tuple)):
                return self.volume in volume
            else:
                return self.volume == volume

    def starts_with(self, starts_with=constants.ANY_LETTER):
        # Если аргумент starts_with не передан, то выбираем все статьи
        if starts_with is constants.ANY_LETTER:
            return True
        if isinstance(starts_with, str):
            starts_with = [starts_with]
        if isinstance(starts_with, Sequence):
            leading = self.civil_equivalent.lstrip(' =').lower()
            return any(leading.startswith(s.lower())
                       for s in starts_with)
        return False

    def get_absolute_url(self):
        return reverse('single_entry_url', args=[str(self.id)])

    def get_rnc_lexm(self):
        return '|'.join(set(civilrus_convert(ov.idem)
                        for ov in self.orth_vars))

    def get_rnc_url(self, lexm=None):
        URL = 'http://processing.ruscorpora.ru/search.xml'
        QUERY_PARAMS = {
            'text': 'lexgramm',
            'mode': 'orthlib',
            'lexm1': self.get_rnc_lexm() if lexm is None else lexm,
        }
        QUERY = '&'.join('{}={}'.format(key, value)
                         for key, value in QUERY_PARAMS.items())
        return '{}?{}'.format(URL, QUERY)

    def resave_all(self, without_mtime=False):
        for o in self.orth_vars:
            o.resave_all(without_mtime=without_mtime)
        for et in self.etymologies:
            et.resave_all(without_mtime=without_mtime)
        for m in self.all_meanings:
            m.resave_all(without_mtime=without_mtime)
        for cg in self.collogroups:
            cg.resave_all(without_mtime=without_mtime)
        for p in self.participles:
            p.resave_all(without_mtime=without_mtime)

    def save(self, without_mtime=False, *args, **kwargs):
        for attr in ('genitive', 'nom_pl', 'short_form', 'sg1', 'sg2'):
            setattr(self, attr, antconc_anticorrupt(getattr(self, attr)))
        orth_vars = self.orth_vars
        if orth_vars:
            self.civil_equivalent = civilrus_convert(orth_vars[0].idem.strip())
            self.civil_inverse = self.civil_equivalent[::-1]
        resave_all = False
        resave_meanings = False
        len_meanings = len(self.meanings)
        first_meaning = self.meanings[0] if len_meanings > 0 else None
        if (len_meanings == 1
                and len(first_meaning.child_meanings) == 0
                and len(first_meaning.examples) == 0
                and len(first_meaning.collogroups) > 0):
            self.restricted_use = True
            resave_meanings = True
        if (len_meanings > 1 or (
                len_meanings == 1 and (len(first_meaning.child_meanings) > 0
                                       or len(first_meaning.examples) > 0))):
            self.restricted_use = False
            resave_meanings = True
        if (self.tmp_volume is None or self.tmp_volume != self.volume):
            if self.volume is None:
                self.volume = 0
            self.tmp_volume = self.volume
            resave_all = True
        if not without_mtime:
            self.mtime = datetime.datetime.now()
        should_log = not self.pk
        super(Entry, self).save(*args, **kwargs)
        if should_log:
            user = get_current_user()
            logger.info('<User: %s> created <Entry id: %s, headword: %s>' % (
                        user and user.last_name or 'No current user',
                        self.id, self.civil_equivalent))
        if resave_all:
            self.resave_all(without_mtime=without_mtime)
        elif resave_meanings:
            for m in self.all_meanings:
                m.save(without_mtime=without_mtime, no_propagate=True)

    def delete(self, *args, **kwargs):
        user = get_current_user()
        logger.info('<User: %s> deleted <Entry id: %s, headword: %s>' % (
                    user and user.last_name or 'No current user',
                    self.id, self.civil_equivalent))
        super(Entry, self).delete(*args, **kwargs)

    def make_double(self):
        with transaction.atomic():
          id1 = self.pk
          e2 = self
          e2.pk = None
          e2.homonym_gloss = ''
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

    def __str__(self):
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
            'hidden',
            'homonym_gloss',
            'homonym_order',
            'id',
            'nom_pl',
            'onym',
            'part_of_speech',
            'participle_type',
            'possessive',
            'restricted_use',
            'sg1',
            'sg2',
            'short_form',
            'status',
            'tantum',
            'template_version',
            'uninflected',
            'volume',
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
        verbose_name = 'словарная статья'
        verbose_name_plural = 'СЛОВАРНЫЕ СТАТЬИ'
        ordering = ('-id',)

class Etymology(models.Model, JSONSerializable, VolumeAttributive):

    entry = ForeignKey(Entry, verbose_name='словарная статья',
                help_text='''Словарная статья, к которой относится данная
                этимология.''', blank=True, null=True,
                on_delete=models.CASCADE)

    collocation = ForeignKey('Collocation', verbose_name='словосочетание',
                help_text='''Словосочетание, к которому относится данная
                этимология.''', blank=True, null=True,
                on_delete=models.CASCADE)

    order = SmallIntegerField('порядок следования', blank=True, default=345)

    etymon_to = ForeignKey('self', verbose_name='этимон для',
                help_text='''Возможный/несомненный этимон для другого этимона,
                который и необходимо указать.''', related_name='etymon_set',
                blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def etymons(self):
        return self.etymon_set.filter(etymon_to=self.id).order_by('order', 'id')

    language = CharField('язык', max_length=1,
                choices=constants.LANGUAGE_CHOICES, default='')

    def is_language(self, x):
        if type(x) in (list, tuple):
            return self.language in [ix
                                     for ix in constants.LANGUAGE_MAP
                                     if ix in x]
        else:
            return self.language == constants.LANGUAGE_MAP[x]

    def has_etymology_language(self):
        return self.language in constants.ETYMOLOGY_LANGUAGES

    def get_etymology_language_cstyle(self):
        return constants.ETYMOLOGY_LANGUAGE_INDESIGN_CSTYLE.get(self.language, '')

    def get_language_css(self):
        return constants.LANGUAGE_CSS[self.language]

    def get_language_translit_css(self):
        return constants.LANGUAGE_TRANSLIT_CSS[self.language]

    text = CharField('языковой эквивалент', max_length=40, blank=True)

    unitext = CharField('языковой эквивалент (Unicode)', max_length=40,
                        blank=True)

    translit = CharField('транслитерация', max_length=40, blank=True)
    meaning = CharField('перевод', max_length=70, blank=True)
    gloss = CharField('пояснение', max_length=70, blank=True)

    source = CharField('документальный источник',
                help_text='например, Септуагинта', max_length=40, blank=True)

    unclear = BooleanField('этимология неясна', default=False)
    questionable = BooleanField('этимология спорна', default=False)
    mark = CharField('грамматическая помета', max_length=20, blank=True)
    additional_info = TextField('примечание', blank=True)
    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
                               blank=True, null=True)

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

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        nfc = unicodedata.normalize('NFC', self.unitext
                                    ).strip().replace('\xad', '')
        if self.unitext != nfc:
            self.unitext = nfc
        super(Etymology, self).save(*args, **kwargs)
        if host_entry is not None and not no_propagate:
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

    def __str__(self):
        return '%s %s %s' % (self.get_language_display(), self.entry,
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
        verbose_name = 'этимон'
        verbose_name_plural = 'этимология'
        ordering = ('id',)


class MeaningContext(models.Model, JSONSerializable, VolumeAttributive):

    meaning = ForeignKey('Meaning', verbose_name='значение',
                         on_delete=models.CASCADE)
    order = SmallIntegerField('порядок следования', blank=True, default=345)

    left_text = CharField('дополнительный текст слева', max_length=50,
            help_text='''Здесь указывается текст на <span class="green"
            >русском</span> языке. Например, если необходим контекст «<span
            class="civil">+</span>&nbsp;<span class="cslav">къ</span
            >&nbsp;<span>class="civil">кому/чему</span>», в данное поле
            добавляется текст&nbsp;«<span class="typing">+</span>».''',
            blank=True)

    context = CharField('текст контекста', max_length=40,
            help_text='''Здесь указывается <span class="green"
            >церковнославянский</span> текст. Например, если необходим контекст
            «<span class="civil">+</span>&nbsp;<span class="cslav">къ</span
            >&nbsp;<span>class="civil">кому/чему</span>», в данное поле
            добавляется текст&nbsp;«<span class="typing">къ</span>».''',
            blank=True)

    @property
    def context_ucs(self):
        return ucs8(self.context)

    right_text = CharField('дополнительный текст справа', max_length=50,
            help_text='''Здесь указывается текст на <span class="green"
            >русском</span> языке. Например, если необходим контекст «<span
            class="civil">+</span>&nbsp;<span class="cslav">къ</span
            >&nbsp;<span>class="civil">кому/чему</span>», в данное поле
            добавляется текст&nbsp;«<span class="typing">кому/чему</span>».''',
            blank=True)

    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
                               blank=True, null=True)
    @property
    def show_in_dictionary(self):
        PL = 'мн.'
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

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        super(MeaningContext, self).save(*args, **kwargs)
        if host_entry is not None and not no_propagate:
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

    def __str__(self):
        SPACE = ' '
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
        verbose_name = 'контекст значения'
        verbose_name_plural = 'контексты значения'


class Meaning(models.Model, JSONSerializable, VolumeAttributive):

    entry_container = ForeignKey(Entry, blank=True, null=True,
            verbose_name='лексема', help_text='''Лексема, к которой
            относится значение. Выберите, только если значение не относится
            к словосочетанию.''', related_name='meaning_set',
            on_delete=models.CASCADE)

    collogroup_container = ForeignKey('CollocationGroup', blank=True, null=True,
            verbose_name='словосочетание', help_text='''Словосочетание,
            к которому относится значение.  Выберите, только если значение не
            относится к конкретной лексеме.''', related_name='meaning_set',
            on_delete=models.CASCADE)

    order = SmallIntegerField('порядок следования', blank=True, default=345)
    parent_meaning = ForeignKey('self', verbose_name='родительское значение',
                    related_name='child_meaning_set', blank=True, null=True,
                    on_delete=models.SET_NULL)

    numex = SmallIntegerField('отображать примеров при значении'
                              'не более чем', blank=True, default=3)
    hidden = BooleanField('Скрыть значение', help_text='''Не отображать
                          данное значение при выводе словарной статьи.''',
                          default=False, editable=False)

    link_to_meaning = ForeignKey('self', verbose_name='ссылка на значение',
                    help_text='''Если значение должно вместо текста содержать
                    только ссылку на другое значение некоторой лексемы или
                    словосочетания, укажите её в данном поле.''',
                    related_name='ref_meaning_set', blank=True, null=True,
                    on_delete=models.SET_NULL)

    link_to_entry = ForeignKey(Entry, verbose_name='ссылка на лексему',
                    help_text='''Если вместо значения должна быть только ссылка
                    на другую словарную статью, укажите её в данном поле.''',
                    related_name='ref_meaning_set', blank=True, null=True,
                    on_delete=models.SET_NULL)

    link_to_collogroup = ForeignKey('CollocationGroup',
            verbose_name='ссылка на словосочетание', help_text='''Если вместо
            значения должна быть только ссылка на целое словосочетание.''',
            related_name='ref_meaning_set', blank=True, null=True,
            on_delete=models.SET_NULL)

    cf_entries = ManyToManyField(Entry, verbose_name='ср. (лексемы)',
                        related_name='cf_meaning_set', blank=True)

    cf_collogroups = ManyToManyField('CollocationGroup',
                        verbose_name='ср. (группы слововосочетаний)',
                        related_name='cf_meaning_set', blank=True)

    cf_meanings = ManyToManyField('self', verbose_name='ср. (значения)',
                        related_name='cf_meaning_set', symmetrical=False,
                        blank=True)

    @property
    def cfmeanings(self):
        return self.cf_meanings.all()

    @property
    def cfentries(self):
        return self.cf_entries.all()

    @property
    def cfcollogroups(self):
        return self.cf_collogroups.all()

    is_valency = BooleanField('содержит управление', default=False)
    metaphorical = BooleanField('гимногр.метафора', default=False)
    figurative = BooleanField('переносное', default=False)
    meaning = TextField('значение', blank=True)

    gloss = TextField('пояснение', help_text='''Для неметафорических
            употреблений/прямых значений здесь указывается энциклопедическая
            информация. Для метафорических/переносных -- (?) разнообразная
            дополнительная информация, комментарии к употреблению.''',
            blank=True)

    substantivus = BooleanField('в роли сущ.', default=False)
    substantivus_type = CharField('форма субстантива', max_length=1,
                                  choices=constants.SUBSTANTIVUS_TYPE_CHOICES,
                                  blank=True, default='')
    substantivus_csl = CharField('цсл форма', max_length=100,
                                 blank=True, default='')

    @property
    def substantivus_csl_ucs(self):
        return apply_to_mixed(ucs8, self.substantivus_csl,
                              CIVIL_IN_CSL_APPLY_TO_CSL)

    @property
    def substantivus_forms(self):
        RE_COMMA = r',\s*'
        return [ucs8(x)
                for x in re.split(RE_COMMA, self.substantivus_csl) if x]

    # только для глаголов
    transitivity = CharField('переходность', max_length=1, blank=True,
                             choices=constants.TRANSITIVITY_CHOICES, default='')

    def is_substantivus_type(self, *slugs):
        return any(
            constants.SUBSTANTIVUS_TYPE_MAP[slug] == self.substantivus_type
            for slug in slugs)

    additional_info = TextField('примечание', help_text='''Любая
            дополнительная информация по данному ЗНАЧЕНИЮ. Дополнительная
            информация по примеру на значение или лексеме указывается не здесь,
            а в аналогичных полях при примере и лексеме, соответственно.''',
            blank=True)

    special_case = CharField('особые случаи', max_length=1,
            choices=constants.MEANING_SPECIAL_CASES_CHOICES,
            blank=True, default='')

    @property
    def has_mcsl(self):
        return '##' in self.meaning or '##' in self.gloss

    def meaning_for_admin(self):
        text = ''
        template = '[<em>%s</em>] '
        if self.figurative:
            text += template % 'перен.'
        if self.metaphorical:
            text += template % 'гимногр.метаф.'
        if self.substantivus:
            text += template % 'в роли сущ.'
        meaning = self.meaning.strip()
        if meaning:
            text += '%s ' % meaning
        gloss = self.gloss.strip()
        if gloss:
            text += '<em>%s</em> ' % gloss
        if self.child_meanings:
            child_meanings = ''
            for m in self.child_meanings:
                child_meanings += '<li>%s</li>' % m.meaning_for_admin()
            text += '<ul>%s</ul>' % child_meanings
        return mark_safe(text)

    def examples_for_admin(self):
        text = ''
        for ex in self.examples:
            text += '<li>%s</li>' % ex.example
        text = '<ol>%s</ol>' % text
        child_meanings = self.child_meanings
        if child_meanings:
            text2 = ''
            for cm in child_meanings:
                text2 += '<li>%s</li>' % cm.examples_for_admin()
            if text2:
                text += '<ul>%s</ul>' % text2
        return mark_safe(text)

    def not_hidden(self):
        host = self.host
        if host:
            return not host.hidden
        return True

    @property
    def examples(self):
        return self.example_set.order_by('wordform_example', 'order', 'id')

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
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
                               blank=True, null=True)
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

    def starts_with(self, starts_with=constants.ANY_LETTER):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.starts_with(starts_with)
        return False

    _RE1 = re.compile(r'[\s,;\\/\(\)]*##[^#]*?##[\s,;\\/\(\)]*|[\s,;\\/\(\)]+',
                      re.UNICODE)
    _RE2 = re.compile(r'[\-'
                      '\u2010\u2011]'
                      r'л\.$|^с$|^инф\.$|^придат\.$'
                      r'|^прям\.$|^речью$'
                      r'|^двойн\.$|^вин\.$',
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

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)
        for mc in self.meaningcontext_set.all():
            mc.resave_all(without_mtime=without_mtime)
        for ex in self.examples:
            ex.resave_all(without_mtime=without_mtime)
        for m in self.child_meanings:
            m.resave_all(without_mtime=without_mtime)
        for cg in self.collogroups:
            cg.resave_all(without_mtime=without_mtime)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        self.substantivus_csl = apply_to_mixed(antconc_anticorrupt,
                self.substantivus_csl, CIVIL_IN_CSL_APPLY_TO_CSL)
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        if self.looks_like_valency(host_entry):
            if self.gloss.strip() and not self.meaning.strip():  #::AUHACK::
                self.meaning = self.gloss
                self.gloss = ''
            self.is_valency = True
        host = self.host
        if (self.numex > 0
                and isinstance(host, CollocationGroup)
                and not host.phraseological
                and host_entry.template_version > 1
                and not host_entry.restricted_use):
            self.numex = -self.numex  # NOTE::INVNUMEX:: Приводим
            # к противоположному значению, чтобы иметь возможность вернуть
            # прежнее значение разрешенных примеров, если условия перестанут
            # соблюдаться.
        if (self.numex < 0 and (
                not isinstance(host, CollocationGroup)
                or host.phraseological
                or host_entry.template_version < 2
                or host_entry.restricted_use)):
            self.numex = -self.numex  #::INVNUMEX::
        super(Meaning, self).save(*args, **kwargs)
        if without_mtime:
            return
        if host_entry is not None and not no_propagate:
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

    def __str__(self):
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
            'numex',
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
        verbose_name = 'значение'
        verbose_name_plural = 'ЗНАЧЕНИЯ'
        ordering = ('id',)


class Example(models.Model, JSONSerializable, VolumeAttributive):

    meaning = ForeignKey(Meaning, verbose_name='значение',
        help_text='Значение, к которому относится данный пример.',
        blank=True, null=True, on_delete=models.SET_NULL)

    entry = ForeignKey(Entry, blank=True, null=True, on_delete=models.CASCADE)
    collogroup = ForeignKey('CollocationGroup',
        blank=True, null=True, on_delete=models.SET_NULL)

    order = SmallIntegerField('порядок следования', blank=True, default=345)
    hidden = BooleanField('Скрыть пример', default=False, editable=False,
        help_text='Не отображать данный пример при выводе словарной статьи.')
    dont_lowercase = BooleanField('Не менять регистр символов',
        help_text='''Не понижать регистр символов. При сохранении у всех
        примеров кроме использующих данный флаг автоматически заглавные
        прописные буквы заменяются на строчные. Данный флаг разрешено
        использовать только в статьях, описывающих единичные буквы.''',
        default=False, editable=False)
    wordform_example = BooleanField(
        'Грамматическая/иная особенность', default=False)

    example = TextField('пример')
    ts_example = TextField(default='')

    @property
    def example_ucs(self):
        return ucs8(self.example)

    context = TextField('широкий контекст',
        help_text='Более широкий контекст для примера', blank=True)

    @property
    def context_ucs(self):
        c = self.context
        e = ucs8(self.example)
        if c:
            c = ucs8(c)
            x, y, z = c.partition(e)
            if y:
                # Разбиение дало положительный результат,
                # в "y" помещён сам пример.
                return (x, y, z)
        return ('', e, '')

    address_text = CharField('адрес', max_length=300, blank=True)

    @property
    def greek_equivs(self):
        return self.greq_set.all().order_by('order', 'id')

    @property
    def translations(self):
        return self.translation_set.all().order_by('order', 'id')

    def greek_equivs_with_numbers(self, show_info=False):
        # Если не надо отображать авторские комментарии, то выводим
        # только реальные греч. параллели с заполненным полем unitext
        # либо с пометой "в греч. иначе", остальные пропускаем.
        if show_info:
            lst = list(self.greek_equivs)
        else:
            lst = [ge for ge in self.greek_equivs
                      if ge.unitext.strip() or ge.aliud]
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
                if ge.unitext == ge_prev.unitext or ge.aliud and ge_prev.aliud:
                    n += 1
                else:
                    groups.append((ge_prev, n))
                    ge_prev = ge
                    n = 1
            groups.append((ge_prev, n))
        assert sum(x[1] for x in groups) == L, 'Число параллелей д.б постоянным'
        return groups

    audited = BooleanField('Пример прошел проверку или взят на проверку',
                           default=False)
    audited_time = DateTimeField('Когда пример был проверен', blank=True,
            editable=False, null=True)

    note = TextField('комментарий', help_text='''Дополнительная
            информация по данному примеру, которая будет видна рядовому
            пользователю словаря''', blank=True)

    additional_info = TextField('примечание', help_text='''Любая
            дополнительная информация по данному ПРИМЕРУ. Дополнительная
            информация по значению или лексеме указывается не здесь,
            а в аналогичных полях при значении и лексеме, соответственно.''',
            blank=True)

    greek_eq_status = CharField('параллели', max_length=1,
            choices=constants.GREEK_EQ_STATUS,
            default=constants.GREEK_EQ_LOOK_FOR)

    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
                               blank=True, null=True)
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

    def starts_with(self, starts_with=constants.ANY_LETTER):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.starts_with(starts_with)
        return False

    def example_for_admin(self):
        text = ''
        return mark_safe(text)

    def ts_convert(self):
        RE = re.compile(
                '[^'
                'абвгдеєжѕзийіклмноѻпрстѹꙋуфхѿцчшщъыьѣюꙗѡѽѧѯѱѳѵ'
                'АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸꙊУФХѾЦЧШЩЪЫЬѢЮꙖѠѼѦѮѰѲѴ'
                r'\~\'\`\^ı'
                ']+')
        ts_text = ''
        for word in re.split(RE, self.example):
            ts_word = word[:1].lower()
            if len(word) > 2:
                ts_word += word[1:-1]
            if len(word) > 1 and word[-1].lower() != 'ъ':
                ts_word += word[-1]
            ts_text += ts_word
        self.ts_example = civilrus_convert(ts_text)

    def angle_brackets(self):
        """ Унификация разных вариантов угловых скобок """
        self.example = re.sub('[<\u3008\u2329\u29fc\u276c\u2770\u276e\uff1c]',
                '\u27e8', self.example)
        self.example = re.sub('[>\u3009\u232a\u29fd\u276d\u2771\u276f\uff1e]',
                '\u27e9', self.example)

    def lowercase_if_necessary(self):
        if self.dont_lowercase:
            return
        r = (
            r'(?:^|(?<=[^'
            r'абвгдеєжѕзийіıклмноѻпрстѹꙋуфхѿцчшщъыьѣюꙗѡѽѧѯѱѳѵ'
            r'АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУꙊФХѾЦЧШЩЪЫЬѢЮꙖѠѼѦѮѰѲѴ~'
            r"\^'`"
            r']))'
            r'([АБВГДЕЄѢЖЗЅИІѴЙКѮЛМНОѺѠѼѾПѰРСТУꙊѸФѲХЦЧШЩЪЫЬЮꙖѦ])'
        )
        segments = re.split(r, self.example)
        if len(segments) > 1:
            example = ''
            for i, s in enumerate(segments):
                if i % 2 == 0:
                    example += s
                elif s == 'Е':
                    example += 'є'
                else:
                    example += s.lower()
            self.example = example

    def get_url_fragment(self):
        return 'ex{0}'.format(self.id)

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)
        for t in self.translation_set.all():
            t.resave_all(without_mtime=without_mtime)
        for ge in self.greek_equivs:
            ge.resave_all(without_mtime=without_mtime)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        self.lowercase_if_necessary()
        self.angle_brackets()
        self.ts_convert()
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
            self.entry = host_entry
        host = self.host
        if host and 'base_meaning_id' in host.__dict__:
            self.collogroup = host
        if self.greek_eq_status == constants.GREEK_EQ_FOUND and \
                self.greq_set.filter(initial_form='').exists():
            self.greek_eq_status = constants.GREEK_EQ_INITFORM_NEEDED
        super(Example, self).save(*args, **kwargs)
        if without_mtime:
            return
        host_entry = self.host_entry
        if host_entry is not None and not no_propagate:
            host_entry.save(without_mtime=without_mtime)

        if not self.address_text.strip() and len(self.example) < 10:
            # Отслеживаем странные случаи, когда в базе возникают примеры без
            # адреса и с текстом примера из нескольких повторяющихся букв
            # наподобие "ооо", "нннн".
            user = get_current_user()
            logger.error(
                    '<Example id: %s, text: "%s">, '
                    'is corrupted during <User: %s>´s session: '
                    '<Host Object: %s %s>, '
                    '<Host Entry id: %s, headword: %s>' % (
                        self.id, self.example,
                        user and user.last_name or 'No current user',
                        host.__class__.__name__, host.id,
                        host_entry.id, host_entry.civil_equivalent))

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
            'dont_lowercase',
            'entry_id',
            'example',
            'greek_eq_status',
            'hidden',
            'id',
            'meaning_id',
            'note',
            'order',
            'wordform_example',
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

    def __str__(self):
        return '(%s) %s' % (self.address_text, self.example)

    class Meta:
        verbose_name = 'пример'
        verbose_name_plural = 'ПРИМЕРЫ'
        ordering = ('id',)


class Translation(models.Model, JSONSerializable, VolumeAttributive):

    for_example = ForeignKey(Example, related_name='translation_set',
                             on_delete=models.CASCADE)
    fragmented = BooleanField('перевод только части примера', default=False)
    fragment_start = SmallIntegerField('номер слова начала фрагмента',
            blank=True, default=1)
    fragment_end = SmallIntegerField('номер слова конца фрагмента',
            blank=True, default=1000)
    source = CharField('Источник', max_length=1,
            choices=constants.TRANSLATION_SOURCE_CHOICES,
            default=constants.TRANSLATION_SOURCE_DEFAULT)
    order = SmallIntegerField('порядок следования', blank=True, default=345)
    hidden = BooleanField('скрывать перевод', default=True,
            help_text='отображать перевод только в комментариях для авторов')
    translation = TextField('перевод')
    additional_info = TextField('примечание', blank=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
                               blank=True, null=True)
    def source_label(self):
        return constants.TRANSLATION_SOURCE_TEXT.get(self.source, '')

    @property
    def translation_fu(self):
        return '%s%s' % (self.translation[0:1].upper(), self.translation[1:])

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
            'source',
            'translation',
        )
        return dict((key, self.__dict__[key]) for key in _fields)

    def get_url_fragment(self):
        return 't{0}'.format(self.id)

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        # Корректировка интервала фрагментированного перевода, если после
        # правки примера позиционирование перевода протухло. FIXME: правки
        # примеров не отслеживаются так, чтобы можно было перерасчитывать
        # позицию перевода. Перевод механически переносится к предпоследнему
        # слову примера, чтобы автор или редакторы заметили аномалию.
        if self.fragmented:
            fragment_length = self.fragment_end - self.fragment_start + 1
            example = self.for_example.example
            n_words = len(re.split(r'[\s\.…,:;?!\/=«»“”‘’\[\]\(\)]+', example))
            exceeding_length = fragment_length > n_words
            fs_out = self.fragment_start > n_words
            fe_out = self.fragment_end > n_words
            if exceeding_length or fs_out or fe_out:
                self.fragment_start = n_words - 1 or 1
                self.fragment_end = self.fragment_start
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        super(Translation, self).save(*args, **kwargs)
        if host_entry is not None and not no_propagate:
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

    def __str__(self):
        if self.fragmented:
            return '(%s, %s) %s' % (self.fragment_start, self.fragment_end,
                                     self.translation)
        else:
            return self.translation

    class Meta:
        verbose_name = 'перевод'
        verbose_name_plural = 'ПЕРЕВОДЫ'
        ordering = ('id',)


class CollocationGroup(models.Model, JSONSerializable, VolumeAttributive):

    base_entry = ForeignKey(Entry, verbose_name='лексема',
            help_text='''Лексема, при которой будет стоять словосочетание.
            Если есть возможность указать конкретное значение, лучше указать
            вместо лексемы её конкретное значение.''',
            related_name='collocationgroup_set', blank=True, null=True,
            on_delete=models.CASCADE)

    base_meaning = ForeignKey(Meaning, verbose_name='значение',
            help_text='''Значение, при котором будет стоять словосочетание.''',
            related_name='collocationgroup_set', blank=True, null=True,
            on_delete=models.CASCADE)

    phraseological = BooleanField('фразеологизм', default=False)

    link_to_entry = ForeignKey(Entry, verbose_name='ссылка на лексему',
            help_text='''Если вместо значений словосочетания должна быть
            только ссылка на словарную статью, укажите её в данном поле.''',
            related_name='ref_collogroup_set', blank=True, null=True,
            on_delete=models.SET_NULL)

    link_to_meaning = ForeignKey('Meaning', verbose_name='ссылка на значение',
            help_text='''Если вместо значений словосочетания должна быть
            только ссылка на опредленное значение лексемы или словосочетания,
            укажите его в данном поле.''', related_name='ref_collogroup_set',
            blank=True, null=True, on_delete=models.SET_NULL)

    cf_entries = ManyToManyField(Entry, verbose_name='ср. (лексемы)',
            related_name='cf_collogroup_set', blank=True)

    cf_meanings = ManyToManyField(Meaning, verbose_name='ср. (значения)',
            related_name='cf_collogroup_set', blank=True)

    order = SmallIntegerField('порядок следования', blank=True, default=345)
    ctime = DateTimeField(editable=False, auto_now_add=True)
    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
            blank=True, null=True)
    additional_info = TextField('примечание', blank=True)
    hidden = BooleanField('Скрыть словосочетание', help_text='''Не отображать
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

    def starts_with(self, starts_with=constants.ANY_LETTER):
        host_entry = self.host_entry
        if host_entry:
            return host_entry.starts_with(starts_with)
        return False

    def meanings_for_admin(self):
        meanings = self.meanings
        if len(meanings) == 0:
            text = ''
        elif len(meanings) == 1:
            text = meanings[0].meaning_for_admin()
        else:
            text = text2 = ''
            for m in meanings:
                text2 += '<li>%s</li>' % m.meaning_for_admin()
            text += '<ol>%s</ol>' % text2
        if self.metaph_meanings:
            text2 = ''
            for m in self.metaph_meanings:
                text2 += '<li>%s</li>' % m.meaning_for_admin()
            text += '<ul>%s</ul>' % text2
        return mark_safe(text)
    meanings_for_admin.short_description = 'Значения словосочетаний'

    def examples_for_admin(self):
        text = ''
        for m in self.meanings:
            text += m.examples_for_admin()
            if m.child_meanings:
                text2 = ''
                for cm in m.child_meanings:
                    text2 += '<li>%s</li>' % cm.examples_for_admin()
                if text2:
                    text += '<ul>%s</ul>' % text2
        if self.metaph_meanings:
            text2 = ''
            for m in self.metaph_meanings:
                text2 += '<li>%s</li>' % m.examples_for_admin()
            text += '<ul>%s</ul>' % text2
        return mark_safe(text)
    examples_for_admin.short_description = 'Примеры на группу словосочетаний'

    meanings = property(meanings)
    metaph_meanings = property(metaph_meanings)
    all_meanings = property(all_meanings)
    has_meanings = property(has_meanings)

    def get_url_fragment(self):
        return 'cg{0}'.format(self.id)

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)
        for c in self.collocations:
            c.resave_all(without_mtime=without_mtime)
        for m in self.all_meanings:
            m.resave_all(without_mtime=without_mtime)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        super(CollocationGroup, self).save(*args, **kwargs)
        if host_entry is not None and not no_propagate:
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
            'additional_info',
            'base_entry_id',
            'base_meaning_id',
            'id',
            'order',
            'phraseological',
        )
        dct = dict((key, self.__dict__[key]) for key in _fields)
        dct['collocations'] = [c.forJSON() for c in self.collocations]
        dct['meanings'] = [m.forJSON() for m in self.all_meanings]
        dct['unsorted_examples'] = [e.forJSON()
                for e in self.example_set.filter(meaning__isnull=True)]
        return dct

    @property
    def civil_equivalent(self):
        ces = [c.civil_equivalent for c in self.collocations
                                if c.civil_equivalent.strip()]
        if ces:
            return '; '.join(ces)
        return ''

    class Meta:
        verbose_name = 'группа словосочетаний'
        verbose_name_plural = 'ГРУППЫ СЛОВОСОЧЕТАНИЙ'
        ordering = ('-id',)


class Collocation(models.Model, JSONSerializable, VolumeAttributive):

    collogroup = ForeignKey(CollocationGroup,
                            verbose_name='группа словосочетаний',
                            related_name='collocation_set',
                            on_delete=models.CASCADE)

    collocation = CharField('словосочетание', max_length=200)

    @property
    def collocation_ucs(self):
        text = apply_to_mixed(antconc_anticorrupt, self.collocation,
                              CIVIL_IN_CSL_APPLY_TO_CSL)
        return apply_to_mixed(ucs8, text, CIVIL_IN_CSL_APPLY_TO_CSL)

    civil_equivalent = CharField('гражданское написание', max_length=350,
                                 blank=True)
    civil_inverse = CharField('гражд. инв.', max_length=350)

    order = SmallIntegerField('порядок следования', blank=True, default=345)

    @property
    def etymologies(self):
        etyms = self.etymology_set.filter(
                        language__in=constants.ETYMOLOGY_LANGUAGES)
        etyms = list(etyms)
        etyms.sort(key=lambda x: (bool(x.etymon_to), x.order, x.id))
        return etyms

    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
            blank=True, null=True)

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

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)
        for et in self.etymologies:
            et.resave_all(without_mtime=without_mtime)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        self.collocation = apply_to_mixed(antconc_anticorrupt, self.collocation,
                                          CIVIL_IN_CSL_APPLY_TO_CSL)
        self.civil_equivalent = civilrus_convert(self.collocation)
        self.civil_inverse = self.civil_equivalent[::-1]
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        super(Collocation, self).save(*args, **kwargs)
        if host_entry is not None and not no_propagate:
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

    def __str__(self):
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
        verbose_name = 'словосочетание'
        verbose_name_plural = 'ОТДЕЛЬНЫЕ СЛОВОСОЧЕТАНИЯ'
        ordering = ('id',)


class GreekEquivalentForExample(models.Model, JSONSerializable, VolumeAttributive):

    for_example = ForeignKey(Example, related_name='greq_set',
                             on_delete=models.CASCADE)
    unitext = CharField('греч. параллель (Unicode)', max_length=100,
                        blank=True)
    @property
    def processed_text(self):
        return re.sub(r'\(([^а-яА-Я]+?)\)', r'\1', self.unitext)

    mark = CharField('грамматическая помета', max_length=20, blank=True)

    source = CharField('документальный источник', help_text='''Например,
                       Септуагинта или, более узко, разные редакции одного
                       текста.''', max_length=40, blank=True)

    position = SmallIntegerField('позиция в примере', blank=True, default=1000,
            help_text='Номер слова, после которого следует поставить перевод.',
            null=True)

    initial_form = CharField('начальная форма лексемы',
                             max_length=100, blank=True)
    initial_form_phraseology = CharField('начальная форма фразеологизма',
                             max_length=100, blank=True)

    note = TextField('комментарий', help_text='''Любая дополнительная
                     информация по данному греческому эквиваленту, которая
                     будет включена в текст статьи.''',
                     blank=True)

    additional_info = TextField('примечание', help_text='''Любая
                                дополнительная информация по данному
                                греческому эквиваленту, которая в текст
                                статьи не войдет''', blank=True)

    aliud = BooleanField('в греч. иначе', default=False)
    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
            blank=True, null=True)
    order = SmallIntegerField('порядок следования', blank=True, default=345)

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

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        nfc = unicodedata.normalize('NFC', self.unitext
                                    ).strip().replace('\xad', '')
        if self.unitext != nfc:
            self.unitext = nfc
        nfc = unicodedata.normalize('NFC', self.initial_form
                                    ).strip().replace('\xad', '')
        if self.initial_form != nfc:
            self.initial_form = nfc
        nfc = unicodedata.normalize('NFC', self.initial_form_phraseology
                                    ).strip().replace('\xad', '')
        if self.initial_form_phraseology != nfc:
            self.initial_form_phraseology = nfc
        super(GreekEquivalentForExample, self).save(*args, **kwargs)
        example = self.for_example
        if self.unitext.strip() and example.greek_eq_status in (
                constants.GREEK_EQ_LOOK_FOR,
                constants.GREEK_EQ_NOT_FOUND,
                constants.GREEK_EQ_CHECK_ADDRESS,
                constants.GREEK_EQ_MEANING,
                constants.GREEK_EQ_URGENT):
            if self.initial_form.strip():
                example.greek_eq_status = constants.GREEK_EQ_FOUND
            else:
                example.greek_eq_status = constants.GREEK_EQ_INITFORM_NEEDED
            example.save(without_mtime=without_mtime)
        if self.unitext.strip() and not self.initial_form.strip() \
                and example.greek_eq_status == constants.GREEK_EQ_FOUND:
            example.greek_eq_status = constants.GREEK_EQ_INITFORM_NEEDED
            example.save(without_mtime=without_mtime)
        if self.unitext.strip() and self.initial_form.strip() and \
                example.greek_eq_status == constants.GREEK_EQ_INITFORM_NEEDED:
            example.greek_eq_status = constants.GREEK_EQ_FOUND
            example.save(without_mtime=without_mtime)
        if host_entry is not None and not no_propagate:
            host_entry.save(without_mtime=without_mtime)

    def delete(self, without_mtime=False, *args, **kwargs):
        super(GreekEquivalentForExample, self).delete(*args, **kwargs)
        if not self.for_example.greek_equivs.exists():
            example = self.for_example
            example.greek_eq_status = constants.GREEK_EQ_LOOK_FOR
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
        verbose_name = 'греческая параллель для примера'
        verbose_name_plural = 'греческие параллели'
        ordering = ('order', 'id')


class OrthographicVariant(models.Model, JSONSerializable, VolumeAttributive):

    # словарная статья, к которой относится данный орф. вариант
    entry = ForeignKey(Entry, related_name='orthographic_variants', blank=True,
                       null=True, on_delete=models.CASCADE)
    parent = ForeignKey('self', related_name='children', blank=True, null=True,
                        on_delete=models.SET_NULL)
    without_accent = BooleanField('без ударения', default=False)
    reconstructed = BooleanField('реконструирован', default=False)
    questionable = BooleanField('реконструкция вызывает сомнения',
                                default=False)
    untitled_exists = BooleanField('Вариант без титла представлен в текстах',
                                   default=False)
    @property
    def childvars(self):
        childvars = self.children.all()

        # Проверяем есть ли титла в текущей словоформе.
        # Для этого обрезаем начальные пробелы и знаки снятия придыхания.
        var = self.idem.lstrip(' =')
        # Удаляем первый символ, т.к. он может иметь верхний регистр.
        var = var[1:]
        # Смотрим, есть ли титла, при этом намеренно исключаем из поиска
        # паерки (ЪЬ).
        r = re.compile(r'[~АБВГДЕЄЖЗЅИЙІКЛМНОѺПРСТѸУФХѾЦЧШЩѢЫЮꙖѠѼѦѮѰѲѴ]')
        has_no_title = not r.search(var)

        if self.untitled_exists and has_no_title:
            childvars = tuple(childvars) + (self,)
        return childvars

    # сам орфографический вариант
    idem = CharField('написание', max_length=50)
    use = CharField('использование', max_length=50, help_text='''
                    Информация о том, с какими значениями данный вариант
                    связан. Разные варианты написания могут коррелировать
                    с разными значениями, как в случае слов богъ/бг~ъ,
                    агг~лъ/аггелъ.''', default='')
    @property
    def idem_ucs(self):
        return ucs8(self.idem)

    @property
    def idem_letter_ucs(self):
        return ucs_convert_affix(self.idem.lower())

    order = SmallIntegerField('порядок следования', blank=True, default=345)
    no_ref_entry = BooleanField('Не делать отсылочной статьи', default=False)
    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
            blank=True, null=True)

    @property
    def host_entry(self):
        return self.entry

    host = host_entry

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        self.idem = antconc_anticorrupt(self.idem)
        if self.questionable and not self.reconstructed:
            self.reconstructed = True
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        super(OrthographicVariant, self).save(*args, **kwargs)
        if host_entry is not None and not no_propagate:
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

    def __str__(self):
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
        verbose_name = 'вариант'
        verbose_name_plural = 'варианты'
        ordering = ('order', 'id')


class Participle(models.Model, JSONSerializable, VolumeAttributive):

    # словарная статья, к которой относится данная словоформа
    entry = ForeignKey(Entry, blank=True, null=True, on_delete=models.CASCADE)

    PARTICIPLE_CHOICES = constants.PARTICIPLE_CHOICES

    tp = CharField('тип причастия', max_length=2,
            choices=constants.PARTICIPLE_CHOICES)
    idem = CharField('словоформа', max_length=50)

    @property
    def idem_ucs(self):
        return ucs8(self.idem)

    order = SmallIntegerField('порядок следования', blank=True, default=345)
    mtime = DateTimeField(editable=False, auto_now=True)
    volume = SmallIntegerField('том', choices=constants.VOLUME_CHOICES,
            blank=True, null=True)

    @property
    def host_entry(self):
        return self.entry

    host = host_entry

    def resave_all(self, without_mtime=False):
        self.save(without_mtime=without_mtime, no_propagate=True)

    def save(self, without_mtime=False, no_propagate=False, *args, **kwargs):
        self.idem = antconc_anticorrupt(self.idem)
        host_entry = self.host_entry
        if host_entry is not None:
            self.volume = host_entry.volume
        super(Participle, self).save(*args, **kwargs)
        if host_entry is not None and not no_propagate:
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

    def __str__(self):
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
        verbose_name = 'причастие'
        verbose_name_plural = 'причастия'
        ordering = ('order', 'id')


class TempEdit(models.Model):
    entry = ForeignKey(Entry, on_delete=models.CASCADE)
    user = ForeignKey(CustomUser, on_delete=models.CASCADE)
    deadline = DateTimeField()


def get_max_lengths(Model):
    return {f.name: f.max_length
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

field_includes = (
    'Entry.HEADWORD',
)

field_excludes = (
    'Collocation.civil_inverse',
    'Collocation.mtime',
    'Collocation.order',

    'CollocationGroup.ctime',
    'CollocationGroup.order',
    'CollocationGroup.mtime',

    'Entry.civil_inverse',
    'Entry.ctime',
    'Entry.duplicate',
    'Entry.mtime',
    'Entry.status',
    'Entry.word_forms_list',

    'Etymology.mtime',
    'Etymology.order',

    'Example.audited',
    'Example.audited_time',
    'Example.hidden',
    'Example.mtime',
    'Example.order',
    'Example.ts_example',

    'GreekEquivalentForExample.mtime',

    'Meaning.ctime',
    'Meaning.mtime',
    'Meaning.order',

    'MeaningContext.mtime',
    'MeaningContext.order',

    'OrthographicVariant.mtime',

    'Participle.mtime',
)

def gather_model_fields():
    opts = []
    for Model in Models:
        for field in Model._meta.fields:
            if (field.attname != 'id'
                    and not field.attname.endswith('_id')
                    and not field.is_relation):
                value = '{}.{}'.format(Model.__name__, field.attname)
                if value not in field_excludes:
                    opts.append((value, value))
    opts.extend((value, value) for value in field_includes)
    opts.sort()
    return opts


MARKDOWN_HELP = '''

    <p style="font-size: xx-small; margin-bottom: 1em">
    Для курсива, ссылок и абзацев используйте
    <a target="_blank" href="https://docs.google.com/document/d/1onDgE9wkZSGbXZg5V3GdoPx8gQ4fhXe73E7Sn0qvDY4">разметку Markdown</a>.
    В качестве предпросмотра используйте
    <a target="_blank" href="https://markdownlivepreview.com/">Markdown
    Live Preview</a>.</p>

'''


class Tip(models.Model):
    ref = CharField('поле, к которому относится подсказка', max_length=50,
                    choices=gather_model_fields(), primary_key=True)
    text = TextField('подсказка для поля ввода', help_text=MARKDOWN_HELP)

    def html(self):
        return markdown.markdown(self.text)

    def __str__(self):
        scrap = self.text[:50]
        if scrap != self.text:
            scrap += '/…/'
        return '[{}] {}'.format(self.ref, scrap)

    class Meta:
        verbose_name = 'подсказка для поля ввода'
        verbose_name_plural = 'подсказки для полей ввода'
        ordering = ('ref',)

try:
    LETTERS = set(e.civil_equivalent.lstrip(' =*')[0].lower()
                  for e in Entry.objects.all())
except (OperationalError, ProgrammingError):
    LETTERS = []
else:
    LETTERS = list(LETTERS)
    LETTERS.sort()
