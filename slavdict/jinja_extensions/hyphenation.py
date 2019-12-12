''' В основу алгоритма расстановки переносов для церковнославянских слов
была положена теория оптимальности, см. С. 131–155 пособия

  https://publications.hse.ru/books/60879388

  Князев С.В., Пожарицкая С.К. Современный русский литературный язык:
    Фонетика, орфоэпия, графика и орфография: Учебное пособие для вузов. —
    2-е изд., перераб. и доп. — М.: Академический Проект; Гаудеамус, 2011. —
    430 c. — (Gaudeamus).

в особенности разделы «Универсальные принципы организации слога» (с. 139),
«Иерархическая упорядоченность универсальных принципов строения слога» (с. 146)
и «Алгоритм слогоделения в русском языке» (с. 149).
'''
import re

initials = ('сткл', 'встр', 'вспл', 'вскр', 'вскл', 'взбр', 'схв',
'стр', 'ств', 'спр', 'спл', 'смр', 'скр', 'скл', 'скв', 'сдр', 'сгр',
'сгн', 'пск', 'мст', 'мзд', 'мгл', 'здр', 'дхн', 'дск', 'всх', 'вст',
'всп', 'всл', 'вск', 'впр', 'впл', 'вкр', 'вкл', 'взн', 'взл', 'вдр',
'вгл', 'шт', 'шн', 'шл', 'шк', 'шв', 'чт', 'чр', 'цв', 'хр', 'хм',
'хл', 'хв', 'фр', 'фл', 'тщ', 'тр', 'тм', 'тл', 'тк', 'тв', 'сш',
'сч', 'сц', 'сх', 'ст', 'ср', 'сп', 'сн', 'см', 'сл', 'ск', 'сж',
'сд', 'сг', 'св', 'сб', 'рц', 'рж', 'рд', 'пш', 'пч', 'пт', 'пс',
'пр', 'пл', 'нр', 'мщ', 'мш', 'мр', 'мн', 'мл', 'лж', 'лг', 'лб',
'кт', 'кс', 'кр', 'кн', 'кл', 'кд', 'кв', 'зр', 'зн', 'зм', 'зл',
'зд', 'зг', 'зв', 'жр', 'жн', 'жд', 'жг', 'жв', 'дщ', 'дх', 'др',
'дн', 'дм', 'дл', 'дв', 'гр', 'гн', 'гл', 'гд', 'гв', 'вш', 'вч',
'вц', 'вх', 'вт', 'вс', 'вр', 'вп', 'вн', 'вм', 'вл', 'вк', 'вз',
'вж', 'вд', 'вв', 'вб', 'бр', 'бл', 'бд', 'щ', 'ш', 'ч', 'ц', 'х',
'ф', 'т', 'с', 'р', 'п', 'н', 'м', 'л', 'к', 'й', 'з', 'ж', 'д',
'г', 'в', 'б')

stops = 'пткбдг'
affricates = 'чц'
fricatives = 'сшфхщзж'
nasals = 'мн'
liquids = 'рлв'
approximants = 'й'
consonants = [
    stops,
    affricates,
    fricatives,
    nasals,
    liquids,
    approximants,
]
vowels = 'аеиоуыэюя'
nulls = 'ъь'

def distribution_principle(intervocal):
    good = []
    for i in range(len(intervocal)):
        if intervocal[i] in nulls:
            continue
        seg = ''.join(c for c in intervocal[i:] if c not in nulls)
        if seg in initials:
            good.append(i)
    return good

def sonority_scale_principle(intervocal):
    NULL = -100
    representation = []
    for c in intervocal:
        for i, consonant_type in enumerate(consonants):
            if c in consonant_type:
                representation.append(i)
                break
        else:
            if c in nulls:
                representation.append(NULL)
            else:
                raise RuntimeError('Illegal Character')
    wavy = []
    raising = []
    slow = []
    for i in range(len(intervocal)):
        if representation[i] == NULL:
            continue
        tail = [r for r in representation[i:] if r != NULL]
        if not tail:
            continue
        if i > 0:
            head = [r for r in representation[:i] if r != NULL]
        else:
            head = []
        if len(set(tail)) == len(tail) and len(set(head)) == len(head):
            wavy.append(i)
        if tail == sorted(tail):
            raising.append(i)
        if not head or head[-1] + 1 == tail[0]:
            slow.append(i)
    raising = set(wavy) & set(raising) or raising
    good = sorted(set(raising) & set(slow) or raising or slow)
    return good

PRE = 0       # - ставить перенос только перед титлосочетанием
POST = 1      # - только после, если есть согласные
PRE_POST = 2  # - и до, и после
titles = (
    ('спС',    PRE),
    ('пСтл',   POST), # апостол
    ('пСл',    POST), # апостол
    #(u'пСт',    []),  # апос[тол]
    ('бг~',    PRE),
    ('бж~тв',  PRE),
    ('бж~',    PRE),
    ('бжCтв',  PRE),
    ('бз~',    PRE),
    ('бл~г',   PRE),
    ('бл~ж',   PRE),
    ('бл~з',   PRE),
    ('блГв',   PRE),
    ('блгДт',  PRE_POST),
    ('блгСв',  PRE_POST),
    ('блгСл',  PRE),
    ('блгСт',  PRE),
    ('бцД',    PRE),
    ('влДк',   PRE),
    ('влДц',   PRE),
    ('влДчц',  PRE),
    ('влДч',   PRE_POST),
    ('вГл',    POST),
    #(u'вГ',     []),
    ('гг~л',    POST),
    ('гл~г',   PRE),
    ('гл~',    PRE),
    ('глВ',    PRE),
    ('гдСнь',  PRE),
    ('гдСв',   PRE),
    ('гдС',    PRE),
    ('гпСж',   PRE),
    ('дв~д',   PRE_POST),
    ('дв~',    PRE),
    ('двСтв',  PRE),
    ('дс~',    PRE),
    ('дх~',    PRE),
    ('дш~',    PRE),
    #(u'и~с',    PRE),
    ('кр~с',   PRE_POST),
    ('кр~ш',   PRE_POST),
    ('крСт',   PRE_POST),
    ('крС',    PRE),
    ('мДр',    PRE_POST),
    ('мл~тв',  PRE_POST),
    ('млДн',   PRE_POST),
    ('млСр',   PRE_POST),
    ('млСтв',  PRE_POST),
    ('млСтн',  PRE_POST),
    ('млС',    PRE),
    ('мт~р',   PRE_POST),
    ('мт~',    PRE),
    ('мр~т',   PRE_POST),
    #(u'мРк',    PRE), # Имярек
    ('мч~',    PRE),
    ('мцС',    PRE),
    ('нбС',    PRE),
    ('нб~',    PRE),
    ('нлД',    PRE),
    ('нн~',    PRE),
    ("ч~ь",    POST),
    ('првДн',  PRE),
    ('прДтч',  PRE), # Предтеча
    ('прДт',   PRE), # Предтеча
    ('прпДб',  PRE_POST),
    ('прОр',   PRE), # Прор или пророк
    ('прСн',   PRE),
    ('прСт',   PRE),
    ('прчСт',  PRE_POST),
    ('пСкп',   POST), # епископ
    #(u'пСк',    []),
    ('ржСт',   PRE_POST),
    #(u'рСл',    []), # Иерусалим
    ('сл~нц',  PRE),
    ('сл~нч',  PRE_POST),
    ('сн~',    PRE),
    ('сп~с',   PRE_POST),
    ('срДц',   PRE),
    ('срДч',   PRE_POST),
    ('ст~л',   PRE_POST),
    ('ст~',    PRE),
    ('стрСт',  PRE_POST),
    #(u'сХ',     []),
    ('стХр',   PRE_POST),
    ('сщ~',    PRE),

    ('трОц',   PRE_POST),
    ('трОч',   PRE_POST),
    ('трСт',   PRE),
    ('хрСт',   PRE),
    ('цр~к',   PRE_POST),
    ('цр~ц',   PRE),
    ('цр~',    PRE),
    ('црС',    PRE),
    ('чл~',    PRE),
    ('чСт',    PRE),
    ('чтС',    PRE),
    ('чт~л',   POST),

    ('~л',     POST),  # израил
)

def filter_positions(intervocal, r, a, b):
    a = set(a)
    b = set(b)
    for i in sorted(a | b):
        if (i in a and i in b) or (i in a and not (a & b)) or \
                (i in a and len(intervocal[i:]) > 1):
            r.append(i)
    return r

def hyphenate_civil(word):
    if len(word) < 4:
        return word
    RE_VOWEL = re.compile(r'[%s]' % vowels)
    ix = RE_VOWEL.search(word)
    if not ix:
        return word
    else:
        ix = ix.start()
    iy = RE_VOWEL.search(word, ix + 1)
    positions = []
    while iy:
        iy = iy.start()
        intervocal = word[ix+1:iy]
        if not intervocal:
            r = [0]
        elif re.findall(r'[~А-Я]', intervocal):
            r = []
            for title, pos_type in titles:
                index = intervocal.find(title)
                if index > -1:
                    if pos_type in (PRE, PRE_POST):
                        r.append(index)
                    if pos_type in (POST, PRE_POST):
                        cons = intervocal[index + len(title):]
                        a = distribution_principle(cons)
                        try:
                            b = sonority_scale_principle(cons)
                        except RuntimeError:
                            pass
                        else:
                            r = filter_positions(cons, r, a, b)
                    break
            else:
                r = []
        else:
            a = distribution_principle(intervocal)
            try:
                b = sonority_scale_principle(intervocal)
            except RuntimeError:
                ix = iy
                iy = RE_VOWEL.search(word, ix + 1)
                continue
            r = filter_positions(intervocal, [], a, b)
        positions += [i + ix + 1 for i in r]
        ix = iy
        iy = RE_VOWEL.search(word, ix + 1)
    low = 2
    high = len(word) - 2
    positions = [i for i in positions if low <= i <= high]
    positions.sort()
    return positions

UCS8_NON_WORD = r'([\s!"\'()*,\-\./:;\[\]\u007f\u00a0‘’‚‛“”„‟–—¤Є«»¬\u00ad°¶·]+)'
UCS8_DIACRITICS = r'#$%1234568@^_~'
UCS8_MAP = {
    '&': '~',
    '+': 'В',
    '0': 'о',
    '7': '~',
    '9': 'ж~',
    '<': 'Х',
    '=': 'Н',
    '>': 'Р',
    '?': 'Ч',

    'A': 'а',
    'B': 'е',
    'C': 'С',
    'D': 'дС',
    'E': 'е',
    'F': 'ф',
    'G': 'г~',
    'H': 'о',
    'I': 'и',
    'J': 'и',
    'K': 'я',
    'L': 'лД',
    'M': 'и',
    'N': 'о',
    'O': 'о',
    'P': 'пс',
    'Q': 'о',
    'R': 'р~',
    'S': 'я',
    'T': 'от',
    'U': 'у',
    'V': 'в',
    'W': 'о',
    'X': 'кс',
    'Y': 'у',
    'Z': 'я',

    '\\': '~',

    'a': 'а',
    'b': 'О',
    'c': 'С',
    'd': 'Д',
    'e': 'е',
    'f': 'ф',
    'g': 'Г',
    'h': 'ы',
    'i': 'и',
    'j': 'и',
    'k': 'я',
    'l': 'л~',
    'm': 'и',
    'n': 'о',
    'o': 'о',
    'p': 'пс',
    'q': 'о',
    'r': 'рС',
    's': 'я',
    't': 'от',
    'u': 'у',
    'v': 'в',
    'w': 'о',
    'x': 'кс',
    'y': 'у',
    'z': 'я',

    '{': 'у',
    '|': 'я',
    '}': 'и~',
    'Ђ': 'и',
    'Ѓ': 'а',
    'ѓ': 'а',
    '…': 'кс~',
    '†': 'а',
    '‡': 'и',
    '€': 'З',
    '‰': 'я',
    'Љ': 'я',
    '‹': 'и~',
    'Њ': 'о',
    'Ќ': 'у',
    'Ћ': 'я',
    'Џ': 'о',
    'ђ': 'вГ',
    '•': 'Ж',
    '™': 'т~',
    'љ': 'я',
    '›': 'и',
    'њ': 'о',
    'ќ': 'у',
    'ћ': 'я',
    'џ': 'о',
    'Ў': 'у',
    'ў': 'у',
    'Ј': 'и',
    'Ґ': 'а',
    '¦': 'х~',
    '§': 'ч~',
    'Ё': 'е',
    '©': 'с~',
    '®': 'рД',
    'Ї': 'и',
    '±': 'я',
    'І': 'и',
    'і': 'и',
    'ґ': 'а',
    'µ': 'у',
    'ё': 'е',
    '№': 'а~',
    'є': 'е',
    'ј': 'и',
    'Ѕ': 'з',
    'ѕ': 'з',
    'ї': 'и',

    'А': 'а',
    'Б': 'б',
    'В': 'в',
    'Г': 'г',
    'Д': 'д',
    'Е': 'е',
    'Ж': 'ж',
    'З': 'з',
    'И': 'и',
    'Й': 'й',
    'К': 'к',
    'Л': 'л',
    'М': 'м',
    'Н': 'н',
    'О': 'о',
    'П': 'п',
    'Р': 'р',
    'С': 'с',
    'Т': 'т',
    'У': 'у',
    'Ф': 'ф',
    'Х': 'х',
    'Ц': 'ц',
    'Ч': 'ч',
    'Ш': 'ш',
    'Щ': 'щ',
    'Ъ': 'ъ',
    'Ы': 'ы',
    'Ь': 'ь',
    'Э': 'е',
    'Ю': 'ю',
    'Я': 'я',

    'э': 'е',
}

def make_civil(segment):
    positions_map = {}
    civil_word = ''
    ix = 0
    for i, c in enumerate(segment):
        if c in UCS8_DIACRITICS:
            continue
        positions_map[ix] = i
        cc = UCS8_MAP.get(c, c)
        civil_word += cc
        ix += len(cc)
    return civil_word, positions_map

def hyphenate_ucs8(text):
    hyphenated_text = ''
    for i, segment in enumerate(re.split(UCS8_NON_WORD, text)):
        if i % 2 == 0:
            civil_word, positions_map = make_civil(segment)
            positions = hyphenate_civil(civil_word)
            parts = []
            ix = 0
            for j in positions:
                iy = positions_map.get(j, -1)
                if iy > -1:
                    parts.append(segment[ix:iy])
                    ix = iy
            parts.append(segment[ix:])
            segment = '\u00AD'.join(parts)
        hyphenated_text += segment
    return hyphenated_text
