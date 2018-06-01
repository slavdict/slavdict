# coding: utf-8
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

initials = (u'сткл', u'встр', u'вспл', u'вскр', u'вскл', u'взбр', u'схв',
u'стр', u'ств', u'спр', u'спл', u'смр', u'скр', u'скл', u'скв', u'сдр', u'сгр',
u'сгн', u'пск', u'мст', u'мзд', u'мгл', u'здр', u'дхн', u'дск', u'всх', u'вст',
u'всп', u'всл', u'вск', u'впр', u'впл', u'вкр', u'вкл', u'взн', u'взл', u'вдр',
u'вгл', u'шт', u'шн', u'шл', u'шк', u'шв', u'чт', u'чр', u'цв', u'хр', u'хм',
u'хл', u'хв', u'фр', u'фл', u'тщ', u'тр', u'тм', u'тл', u'тк', u'тв', u'сш',
u'сч', u'сц', u'сх', u'ст', u'ср', u'сп', u'сн', u'см', u'сл', u'ск', u'сж',
u'сд', u'сг', u'св', u'сб', u'рц', u'рж', u'рд', u'пш', u'пч', u'пт', u'пс',
u'пр', u'пл', u'нр', u'мщ', u'мш', u'мр', u'мн', u'мл', u'лж', u'лг', u'лб',
u'кт', u'кс', u'кр', u'кн', u'кл', u'кд', u'кв', u'зр', u'зн', u'зм', u'зл',
u'зд', u'зг', u'зв', u'жр', u'жн', u'жд', u'жг', u'жв', u'дщ', u'дх', u'др',
u'дн', u'дм', u'дл', u'дв', u'гр', u'гн', u'гл', u'гд', u'гв', u'вш', u'вч',
u'вц', u'вх', u'вт', u'вс', u'вр', u'вп', u'вн', u'вм', u'вл', u'вк', u'вз',
u'вж', u'вд', u'вв', u'вб', u'бр', u'бл', u'бд', u'щ', u'ш', u'ч', u'ц', u'х',
u'ф', u'т', u'с', u'р', u'п', u'н', u'м', u'л', u'к', u'й', u'з', u'ж', u'д',
u'г', u'в', u'б')

stops = u'пткбдг'
affricates = u'чц'
fricatives = u'сшфхщзж'
nasals = u'мн'
liquids = u'рлв'
approximants = u'й'
consonants = [
    stops,
    affricates,
    fricatives,
    nasals,
    liquids,
    approximants,
]
vowels = u'аеиоуыэюя'
nulls = u'ъь'

def distribution_principle(intervocal):
    good = []
    for i in range(len(intervocal)):
        if intervocal[i] in nulls:
            continue
        seg = u''.join(c for c in intervocal[i:] if c not in nulls)
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
    (u'спС',    PRE),
    (u'пСтл',   POST), # апостол
    (u'пСл',    POST), # апостол
    #(u'пСт',    []),  # апос[тол]
    (u'бг~',    PRE),
    (u'бж~тв',  PRE),
    (u'бж~',    PRE),
    (u'бжCтв',  PRE),
    (u'бз~',    PRE),
    (u'бл~г',   PRE),
    (u'бл~ж',   PRE),
    (u'бл~з',   PRE),
    (u'блГв',   PRE),
    (u'блгДт',  PRE_POST),
    (u'блгСв',  PRE_POST),
    (u'блгСл',  PRE),
    (u'блгСт',  PRE),
    (u'бцД',    PRE),
    (u'влДк',   PRE),
    (u'влДц',   PRE),
    (u'влДчц',  PRE),
    (u'влДч',   PRE_POST),
    (u'вГл',    POST),
    #(u'вГ',     []),
    (u'гг~л',    POST),
    (u'гл~г',   PRE),
    (u'гл~',    PRE),
    (u'глВ',    PRE),
    (u'гдСнь',  PRE),
    (u'гдСв',   PRE),
    (u'гдС',    PRE),
    (u'гпСж',   PRE),
    (u'дв~д',   PRE_POST),
    (u'дв~',    PRE),
    (u'двСтв',  PRE),
    (u'дс~',    PRE),
    (u'дх~',    PRE),
    (u'дш~',    PRE),
    #(u'и~с',    PRE),
    (u'кр~с',   PRE_POST),
    (u'кр~ш',   PRE_POST),
    (u'крСт',   PRE_POST),
    (u'крС',    PRE),
    (u'мДр',    PRE_POST),
    (u'мл~тв',  PRE_POST),
    (u'млДн',   PRE_POST),
    (u'млСр',   PRE_POST),
    (u'млСтв',  PRE_POST),
    (u'млСтн',  PRE_POST),
    (u'млС',    PRE),
    (u'мт~р',   PRE_POST),
    (u'мт~',    PRE),
    (u'мр~т',   PRE_POST),
    #(u'мРк',    PRE), # Имярек
    (u'мч~',    PRE),
    (u'мцС',    PRE),
    (u'нбС',    PRE),
    (u'нб~',    PRE),
    (u'нлД',    PRE),
    (u'нн~',    PRE),
    (u"ч~ь",    POST),
    (u'првДн',  PRE),
    (u'прДтч',  PRE), # Предтеча
    (u'прДт',   PRE), # Предтеча
    (u'прпДб',  PRE_POST),
    (u'прОр',   PRE), # Прор или пророк
    (u'прСн',   PRE),
    (u'прСт',   PRE),
    (u'прчСт',  PRE_POST),
    (u'пСкп',   POST), # епископ
    #(u'пСк',    []),
    (u'ржСт',   PRE_POST),
    #(u'рСл',    []), # Иерусалим
    (u'сл~нц',  PRE),
    (u'сл~нч',  PRE_POST),
    (u'сн~',    PRE),
    (u'сп~с',   PRE_POST),
    (u'срДц',   PRE),
    (u'срДч',   PRE_POST),
    (u'ст~л',   PRE_POST),
    (u'ст~',    PRE),
    (u'стрСт',  PRE_POST),
    #(u'сХ',     []),
    (u'стХр',   PRE_POST),
    (u'сщ~',    PRE),

    (u'трОц',   PRE_POST),
    (u'трОч',   PRE_POST),
    (u'трСт',   PRE),
    (u'хрСт',   PRE),
    (u'цр~к',   PRE_POST),
    (u'цр~ц',   PRE),
    (u'цр~',    PRE),
    (u'црС',    PRE),
    (u'чл~',    PRE),
    (u'чСт',    PRE),
    (u'чтС',    PRE),
    (u'чт~л',   POST),

    (u'~л',     POST),  # израил
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
    RE_VOWEL = re.compile(ur'[%s]' % vowels)
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
        elif re.findall(ur'[~А-Я]', intervocal):
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
    return positions

UCS8_NON_WORD = ur'([\s!"\'()*,\-\./:;\[\]\u007f\u00a0‘’‚‛“”„‟–—¤Є«»¬\u00ad°¶·]+)'
UCS8_DIACRITICS = ur'#$%1234568@^_~'
UCS8_MAP = {
    u'&': u'~',
    u'+': u'В',
    u'0': u'о',
    u'7': u'~',
    u'9': u'ж~',
    u'<': u'Х',
    u'=': u'Н',
    u'>': u'Р',
    u'?': u'Ч',

    u'A': u'а',
    u'B': u'е',
    u'C': u'С',
    u'D': u'дС',
    u'E': u'е',
    u'F': u'ф',
    u'G': u'г~',
    u'H': u'о',
    u'I': u'и',
    u'J': u'и',
    u'K': u'я',
    u'L': u'лД',
    u'M': u'и',
    u'N': u'о',
    u'O': u'о',
    u'P': u'пс',
    u'Q': u'о',
    u'R': u'р~',
    u'S': u'я',
    u'T': u'от',
    u'U': u'у',
    u'V': u'в',
    u'W': u'о',
    u'X': u'кс',
    u'Y': u'у',
    u'Z': u'я',

    u'\\': u'~',

    u'a': u'а',
    u'b': u'О',
    u'c': u'С',
    u'd': u'Д',
    u'e': u'е',
    u'f': u'ф',
    u'g': u'Г',
    u'h': u'ы',
    u'i': u'и',
    u'j': u'и',
    u'k': u'я',
    u'l': u'л~',
    u'm': u'и',
    u'n': u'о',
    u'o': u'о',
    u'p': u'пс',
    u'q': u'о',
    u'r': u'рС',
    u's': u'я',
    u't': u'от',
    u'u': u'у',
    u'v': u'в',
    u'w': u'о',
    u'x': u'кс',
    u'y': u'у',
    u'z': u'я',

    u'{': u'у',
    u'|': u'я',
    u'}': u'и~',
    u'Ђ': u'и',
    u'Ѓ': u'а',
    u'ѓ': u'а',
    u'…': u'кс~',
    u'†': u'а',
    u'‡': u'и',
    u'€': u'З',
    u'‰': u'я',
    u'Љ': u'я',
    u'‹': u'и~',
    u'Њ': u'о',
    u'Ќ': u'у',
    u'Ћ': u'я',
    u'Џ': u'о',
    u'ђ': u'вГ',
    u'•': u'Ж',
    u'™': u'т~',
    u'љ': u'я',
    u'›': u'и',
    u'њ': u'о',
    u'ќ': u'у',
    u'ћ': u'я',
    u'џ': u'о',
    u'Ў': u'у',
    u'ў': u'у',
    u'Ј': u'и',
    u'Ґ': u'а',
    u'¦': u'х~',
    u'§': u'ч~',
    u'Ё': u'е',
    u'©': u'с~',
    u'®': u'рД',
    u'Ї': u'и',
    u'±': u'я',
    u'І': u'и',
    u'і': u'и',
    u'ґ': u'а',
    u'µ': u'у',
    u'ё': u'е',
    u'№': u'а~',
    u'є': u'е',
    u'ј': u'и',
    u'Ѕ': u'з',
    u'ѕ': u'з',
    u'ї': u'и',

    u'А': u'а',
    u'Б': u'б',
    u'В': u'в',
    u'Г': u'г',
    u'Д': u'д',
    u'Е': u'е',
    u'Ж': u'ж',
    u'З': u'з',
    u'И': u'и',
    u'Й': u'й',
    u'К': u'к',
    u'Л': u'л',
    u'М': u'м',
    u'Н': u'н',
    u'О': u'о',
    u'П': u'п',
    u'Р': u'р',
    u'С': u'с',
    u'Т': u'т',
    u'У': u'у',
    u'Ф': u'ф',
    u'Х': u'х',
    u'Ц': u'ц',
    u'Ч': u'ч',
    u'Ш': u'ш',
    u'Щ': u'щ',
    u'Ъ': u'ъ',
    u'Ы': u'ы',
    u'Ь': u'ь',
    u'Э': u'е',
    u'Ю': u'ю',
    u'Я': u'я',

    u'э': u'е',
}

def make_civil(segment):
    positions_map = {}
    civil_word = u''
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
    hyphenated_text = u''
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
            segment = u'\u00AD'.join(parts)
        hyphenated_text += segment
    return hyphenated_text
