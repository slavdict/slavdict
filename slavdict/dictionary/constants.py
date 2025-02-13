from slavdict.dictionary.utils import volume_label

MOCK_ORTHVAR = '-]*[-'

NBSP = '\u00A0'  # неразрывный пробел

BLANK_CHOICE = (('', ''),)

PART_OF_SPEECH_CHOICES = (
    ('a', 'сущ.'),
    ('b', 'прил.'),
    ('c', 'мест.'),
    ('d', 'гл.'),
    # 'e' used to be used for deprecated Participle part of speech
    ('f', 'нареч.'),
    ('g', 'союз'),
    ('h', 'предл.'),
    ('i', 'част.'),
    ('j', 'межд.'),
    ('k', 'числ.'),
    ('l', '[буква]'),
    ('m', 'прич.-прил.'),
    ('n', 'предик. нареч.'),
    ('e', 'предик. прил.'),
    ('o', 'транслит.'),
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
    'particle': 'i',
    'postposition': 'h',
    'predicative-adjective': 'e',
    'predicative-adverb': 'n',  # NOTE: В мнемониках нельзя использовать
    # пробелы, поскольку названия используются в частности для CSS-классов.
    # Поэтому "predicative-adverb", а не "predicative adverb".
    'preposition': 'h',
    'pronoun': 'c',
    'translit': 'o',
    'verb': 'd',
}
# Порядок отображения частей речи при выводе статей с группировкой
# по части речи
PART_OF_SPEECH_ORDER = (
    PART_OF_SPEECH_MAP['letter'],
    PART_OF_SPEECH_MAP['number'],
    PART_OF_SPEECH_MAP['translit'],
    PART_OF_SPEECH_MAP['noun'],
    PART_OF_SPEECH_MAP['pronoun'],
    PART_OF_SPEECH_MAP['adjective'],
    PART_OF_SPEECH_MAP['participle-adjective'],
    PART_OF_SPEECH_MAP['predicative-adjective'],
    PART_OF_SPEECH_MAP['predicative-adverb'],
    PART_OF_SPEECH_MAP['adverb'],
    PART_OF_SPEECH_MAP['adposition'],
    PART_OF_SPEECH_MAP['preposition'],
    PART_OF_SPEECH_MAP['postposition'],
    PART_OF_SPEECH_MAP['conjunction'],
    PART_OF_SPEECH_MAP['interjection'],
    PART_OF_SPEECH_MAP['particle'],
    PART_OF_SPEECH_MAP['verb'],
)
ALWAYS_LAST_POS = 100


TANTUM_CHOICES = (
    ('d', 'только дв.'),
    ('p', 'только мн.'),
)
TANTUM_MAP = {
    'dualeTantum': 'd',
    'pluraleTantum': 'p',
}

GENDER_CHOICES = (
    ('m', 'м.'),
    ('f', 'ж.'),
    ('n', 'с.'),
    ('d', 'м. и' + NBSP + 'ж.'),
)
GENDER_MAP = {
    'masculine': 'm',
    'feminine': 'f',
    'neutral': 'n',
    'dual': 'd',
}

ONYM_CHOICES = (
    ('', 'не имя собст.'),
    ('a', 'имя'),
    ('b', 'топоним'),
    ('c', 'народ/общность людей'),
    ('d', '[другое]'),
)
ONYM_MAP = {
    'anthroponym': 'a',
    'toponym': 'b',
    'ethnonym': 'c',
    'other': 'd',
}

TRANSITIVITY_CHOICES = (
    ('', ''),
    ('t', 'перех.'),
    ('i', 'неперех.'),
    ('b', 'перех. и неперех.'),
)
TRANSITIVITY_MAP = {
    'transitive': 't',
    'intransitive': 'i',
    'labile': 'b',
}

# TODO: Должен остаться только один
# из этих двух списков для причастий.
PARTICIPLE_TYPE_CHOICES = (
    ('a', 'действ. прич. наст. вр.'),
    ('b', 'действ. прич. прош. вр.'),
    ('c', 'страд. прич. наст. вр.'),
    ('d', 'страд. прич. прош. вр.'),
)
PARTICIPLE_CHOICES = (
    ('1', 'действ. наст.'),
    ('2', 'действ. прош.'),
    ('3', 'страд. наст.'),
    ('4', 'страд. прош.'),
)
PARTICIPLE_TYPE_MAP = {
    'pres_act': 'a',
    'perf_act': 'b',
    'pres_pass': 'c',
    'perf_pass': 'd',
}

STATUS_CHOICES = (
    ('c', 'создана'),
    ('w', 'в работе'),
    ('g', 'поиск греч.'),
    ('f', 'завершена'),
    ('e', 'редактируется'),
    ('a', 'утверждена'),
)
DEFAULT_ENTRY_STATUS = 'c'
STATUS_MAP = {
    'approved': 'a',
    'beingEdited': 'e',
    'created': 'c',
    'finished': 'f',
    'greek': 'g',
    'inWork': 'w',
}
HELLINIST_BAD_STATUSES = (
    STATUS_MAP['created'],
    STATUS_MAP['inWork'],
)

LANGUAGE_CHOICES = (
    ('a', 'греч.'),
    ('b', 'ивр.'),
    ('c', 'аккад.'),
    ('d', 'арам.'),
    ('e', 'арм.'),
    ('f', 'груз.'),
    ('g', 'копт.'),
    ('h', 'лат.'),
    ('i', 'сир.'),
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
ETYMOLOGY_LANGUAGES = list(ETYMOLOGY_LANGUAGE_INDESIGN_CSTYLE.keys())
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
    ('a', 'с.' + NBSP + 'ед.'),
    ('b', 'с.' + NBSP + 'мн.'),
    ('c', 'м.' + NBSP + 'ед.'),
    ('d', 'м.' + NBSP + 'мн.'),
    ('e', 'ж.' + NBSP + 'ед.'),
    ('f', 'ж.' + NBSP + 'мн.'),
)
SUBSTANTIVUS_TYPE_MAP = {
    'n.sg.': 'a',
    'n.pl.': 'b',
    'm.sg.': 'c',
    'm.pl.': 'd',
    'f.sg.': 'e',
    'f.pl.': 'f',
}

GREEK_EQ_LOOK_FOR = 'L'  # Следует найти греческие параллели для примера
GREEK_EQ_STOP = 'S'  # Греческие параллели не нужны
GREEK_EQ_CHECK_ADDRESS = 'C'
    # Необходимо уточнить адрес примера, чтобы грецист смог найти пример
GREEK_EQ_NOT_FOUND = 'N'  # Греч.параллель для примера найти не удалось
GREEK_EQ_FOUND = 'F'  # Греч.параллель для примера найдена
GREEK_EQ_FOUND_ONLY_FOR_COLLOGROUP = 'O'  # Греч.параллель для примера найдена,
    # но она относится только ко целому словосочетанию. Это случаи вроде того,
    # когда в статье "делати" словосочетанию "делати землю" соответствует
    # не словосочетание, а одиночное греч. слово. Или "деяти молитву" (греч.
    # προσεύχομαι) в статье "деяти".
GREEK_EQ_INITFORM_NEEDED = 'I'  # Греч.параллель для примера найдена, но
    # начальная форма для греческого индекса не указана
GREEK_EQ_POSTPONED = 'P'  # Нахождение греч. параллели отложено, например,
    # потому что у грециста в данный момент нет греч. текста, но впоследствии
    # может появиться.
GREEK_EQ_MEANING = 'M'
    # Греч.параллели для примера нужны, чтобы определить значение слова
GREEK_EQ_URGENT = 'U'  # Греч.параллели для примера нужны в срочном порядке

GREEK_EQ_STATUS = (
    (GREEK_EQ_LOOK_FOR, 'следует найти'),
    (GREEK_EQ_STOP, 'не нужны'),
    (GREEK_EQ_CHECK_ADDRESS, 'уточнить адрес'),
    (GREEK_EQ_NOT_FOUND, 'найти не удалось'),
    (GREEK_EQ_POSTPONED, 'когда-нибудь позже, отложенные на потом'),
    (GREEK_EQ_FOUND, 'найдены'),
    (GREEK_EQ_FOUND_ONLY_FOR_COLLOGROUP, 'найдены (только для словосочетания)'),
    (GREEK_EQ_INITFORM_NEEDED, 'найдены (без указания начальных форм)'),
    (GREEK_EQ_MEANING, 'необходимы для опр-я значения'),
    (GREEK_EQ_URGENT, 'срочное'),
)


TRANSLATION_SOURCES = (
    (TRANSLATION_SOURCE_NULL     := '',  None,                       ''),

    (TRANSLATION_SOURCE_SYNODAL  := 'S', 'в\u00a0Син. пер.',         'Синодальный перeвод'),
    (TRANSLATION_SOURCE_RBS      := 'R', 'в\u00a0пер. РБО',          'Перевод РБО'),
    (TRANSLATION_SOURCE_RBS1824  := '4', 'в\u00a0пер. РБО 1824',     'Перевод РБО 1824 г.'),
    (TRANSLATION_SOURCE_PSTGU    := 'U', 'в\u00a0пер. ПСТГУ',        'Перевод ПСТГУ'),
    (TRANSLATION_SOURCE_MONREAL  := 'M', 'в\u00a0пер. БПИП',         'Перевод братства преп. Иова Почаевского'),
    # Житие преподобныя матери нашея Марии Египетския. — Монреаль: Издание Братства преп. Иова Почаевскаго РПЦЗ, 1980.

    (TRANSLATION_SOURCE_AVERINC  := 'C', 'в\u00a0пер. Авер.',        ' Аверинцев С.С. — библ. переводы'),
    (TRANSLATION_SOURCE_ADAMENKO := 'A', 'в\u00a0пер. Адам.',        ' Адаменко В., свящ.'),
    (TRANSLATION_SOURCE_ADAMENKO := 'F', 'в\u00a0пер. Алф.',         '(Алфеев) Иларион — пер. Литургии'),
    (TRANSLATION_SOURCE_BEZOBRAZ := 'Z', 'в\u00a0пер. Безобр.',      '(Безобразов) Кассиан, еп.'),
    (TRANSLATION_SOURCE_BIRUKOVY := 'B', 'в\u00a0пер. Бир.',         ' Бируковы'),
    (TRANSLATION_SOURCE_VINZHELT := 'I', 'в\u00a0пер. Вин. и Желт.', ' Виноградов А.Ю., Желтов М., свящ. — пер. Литургии'),
    (TRANSLATION_SOURCE_VOLOXON  := 'X', 'в\u00a0пер. Вол.',         ' Волохонский А. — пер. богослуж. текстов и псалмов'),
    (TRANSLATION_SOURCE_GLUXAREV := '1', 'в\u00a0пер. Глух.',        '(Глухарев) Макарий, архим. — пер. Ветхого Завета'),
    (TRANSLATION_SOURCE_GOVOROV  := 'G', 'в\u00a0пер. Говор.',       '(Говоров) Феофан, еп. — пер. Добротолюбия'),
    (TRANSLATION_SOURCE_DESNIC   := '5', 'в\u00a0пер. Десн.',        ' Десницкий А. — библ. переводы'),
    (TRANSLATION_SOURCE_DURASOV  := 'D', 'в\u00a0пер. Дурас.',       ' Дурасов С. — пер. канонов'),
    (TRANSLATION_SOURCE_ELECKIX  := '6', 'в\u00a0пер. Елец.',        '(Елецких) Ионафан, архиеп. — пер. Великого канона'),
    (TRANSLATION_SOURCE_KEDROV   := 'K', 'в\u00a0пер. Кедр.',        ' Кедров Н. — пер. великого канона'),
    (TRANSLATION_SOURCE_KULAKOV  := 'V', 'в\u00a0пер. Кул.',         ' Кулаков М.П. — пер. Нового Завета (Институт перевода Библии в Заокском)'),
    (TRANSLATION_SOURCE_LOVJAG1  := 'L', 'в\u00a0пер. Е.\u202fЛов.', ' Ловягин Е.И. — пер. канонов'),
    (TRANSLATION_SOURCE_LOVJAG2  := '2', 'в\u00a0пер. И.\u202fЛов.', ' Ловягин И.Ф. — пер. октоиха'),
    (TRANSLATION_SOURCE_NAXIMOV  := 'N', 'в\u00a0пер. Нахим.',       ' Нахимов Н. (Зайончковский Н.Ч.)'),
    (TRANSLATION_SOURCE_PALEX    := 'E', 'в\u00a0пер. Пал.',         ' Палехов Г. — пер. Известия учительного'),
    (TRANSLATION_SOURCE_POBED    := '#', 'в\u00a0пер. Поб.',         ' Победоносцев К.П. — пер. Нового Завета'),
    (TRANSLATION_SOURCE_POLAKOV  := '7', 'в\u00a0пер. Поляк.',       ' Полякова С. — пер. Жития Марии Египетской'),
    (TRANSLATION_SOURCE_POLANSK  := 'P', 'в\u00a0пер. Пол.',         '(Полянский) Иустин, еп. — пер. Алфавита духовного'),
    (TRANSLATION_SOURCE_SVIRELIN := '8', 'в\u00a0пер. Свир.',        ' Свирелин А., прот. — пер. Последования к причащению'),
    (TRANSLATION_SOURCE_SEDAKOVA := '3', 'в\u00a0пер. Сед.',         ' Седакова О.А.'),                                                             
    (TRANSLATION_SOURCE_SKABAL   := '*', 'в\u00a0пер. Скбл.',        ' Скабалланович М.Н. — пер. праздников'),
    (TRANSLATION_SOURCE_TIMROT   := 'T', 'в\u00a0пер. Тимр.',        '(Тимрот) Амвросий, иером.'),                                                  
    (TRANSLATION_SOURCE_TUMANOV  := '9', 'в\u00a0пер. Тум.',         '(Туманов) Силуан, игум.'), 
    (TRANSLATION_SOURCE_JUNGEROV := 'J', 'в\u00a0пер. Юнг.',         ' Юнгеров П.А.'),

    (TRANSLATION_SOURCE_ZERO     := '0', 'в пер. Zero',              '[перевода нет в списке]'),
)

TRANSLATION_SOURCE_DEFAULT = TRANSLATION_SOURCE_NULL
TRANSLATION_SOURCE_TEXT = {slug: mark for slug, mark, _ in TRANSLATION_SOURCES if mark is not None}
TRANSLATION_SOURCE_CHOICES = [(slug, label) for slug, _, label in TRANSLATION_SOURCES if label is not None]

assert len(TRANSLATION_SOURCE_CHOICES) == \
       len(set(value.upper() for value, label in TRANSLATION_SOURCE_CHOICES))

SC1, SC2, SC3, SC4, SC5, SC6, SC7, SC8, SC9, SC10 = 'abcdefghij'
ENTRY_SPECIAL_CASES = SC1, SC2, SC3, SC4, SC5, SC6, SC7, SC8, SC9, SC10
ENTRY_SPECIAL_CASES_CHOICES = (
    ('', ''),
    (SC1, 'Несколько лексем одного рода'),
    (SC2, '2 лексемы, муж. и жен. рода'),
    (SC10, '2 лексемы, муж. и ср. рода'),
    (SC3, '2 лексемы, ср. и жен. рода'),
    (SC7, '2 лексемы, жен. и ср. рода'),
    (SC4, '2 лексемы, жен. и только мн.'),
    (SC5, '2 лексемы, только мн. и жен.'),
    (SC6, '3 лексемы, 3 муж. и последний неизм.'),
    (SC8, '4 лексемы [вихрь]'),
    (SC9, 'Вынудить отображение пометы «неперех. и перех.» '
          'при равном кол-ве перех. и неперех. значений'),
)
MSC1, MSC2, MSC3, MSC4, MSC5, MSC6, MSC7, MSC8, MSC9, MSC10 = 'abcdefghij'
MSC11, MSC12, MSC13, MSC14, MSC15, MSC16, MSC17, MSC18, MSC19 = 'klmnopqrs'
MSC20, MSC21, MSC22, MSC23, MSC24 = 'tuvwx'
MEANING_SPECIAL_CASES_CHOICES = (
    ('', ''),
    ('Имена', (
        (MSC1,  'канонич.'),
        (MSC8,  'имя собств.'),
        (MSC9,  'топоним'),
    )),
    ('Части речи', (
        (MSC22, 'мест.'),
        (MSC6,  'нареч.'),
        (MSC19, 'предик. нареч.'),
        (MSC13, 'союз'),
        (MSC2,  'предл.'),
        (MSC3,  'част.'),
        (MSC7,  'межд.'),
    )),
    ('Формы слова', (
        (MSC4,  'дат.'),
        (MSC11, 'мн.'),
        (MSC5,  'твор. ед. в роли нареч.'),
        (MSC12, 'в роли нареч.'),
        (MSC14, 'в роли прил.'),
        (MSC24, 'в роли действ. прич.'),
        (MSC23, 'в роли мест.'),
        (MSC20, 'в роли союза'),
        (MSC15, 'в роли част.'),
    )),
    ('Другое', (
        (MSC17, 'безл.'),  # Безличное употребление глагола
        (MSC18, 'вводн.'),
        (MSC21, 'плеоназм'),
        (MSC16, 'полувспом.'),  # Полувспомогательный глагол
        (MSC10, 'преимущ.'),
    )),
)
MSC_ROLE_FORM_POS = (MSC5,)
MSC_ROLE_POS = (MSC12, MSC14, MSC15, MSC20, MSC23, MSC24)
MSC_ROLE = MSC_ROLE_FORM_POS + MSC_ROLE_POS
POS_SPECIAL_CASES = (MSC2, MSC3, MSC6, MSC7, MSC13, MSC19, MSC22)
POS_SPECIAL_CASES_MAP = {
    MSC2: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['preposition']],
    MSC3: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['particle']],
    MSC6: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['adverb']],
    MSC7: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['interjection']],
    MSC13: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['conjunction']],
    MSC19: dict(PART_OF_SPEECH_CHOICES)[
        PART_OF_SPEECH_MAP['predicative-adverb']],
    MSC22: dict(PART_OF_SPEECH_CHOICES)[PART_OF_SPEECH_MAP['pronoun']],
}

YET_NOT_IN_VOLUMES = None
WHOLE_DICTIONARY = False
VOLUME_LETTERS = {
    1: ('а', 'б'),
    2: ('в',),
    3: ('г', 'д', 'е'),
    4: ('ж', 'з'),
    5: ('и',),
    6: ('к',),
    7: ('л', 'м'),
    8: ('н',),
    9: ('о',),
    10: ('п',),
    11: ('р', 'с'),
    12: ('т', 'у', 'ф', 'х', 'ц', 'ч', 'ш', 'щ', 'ю', 'я'),
}
ANY_LETTER = None
LOCKED_LETTERS = VOLUME_LETTERS[1] + VOLUME_LETTERS[2] + VOLUME_LETTERS[3]
CURRENT_VOLUME = 5
NO_VOLUME_CHOICE = 0
DEFAULT_VOLUME_CHOICE = NO_VOLUME_CHOICE
VOLUME_CHOICES = (
    (NO_VOLUME_CHOICE, 'Вне томов'),
) + tuple(
    (key, volume_label(key, value))
    for key, value in sorted(VOLUME_LETTERS.items())
)
