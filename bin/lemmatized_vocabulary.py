import os
import re
import sys

import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict.dictionary.utils import antconc_wordform_query
from slavdict.dictionary.utils import civilrus_convert
from slavdict.dictionary.utils import resolve_titles

path = os.path.expanduser('~/Documents/slavdict_slovnik')
lem_files = ('lem-1.csv', 'lem-2.csv', 'lem-3.csv', 'lem-4.csv', 'lem-5.csv')
words_basic_corpus_filename = 'corpus_without_bible.txt'
words_bible_corpus_filename = 'corpus_bible_only.txt'


def load_data(f):
    f.readline()
    data = []
    for line in f.readlines():
        sort, lex, pos, flextype, gram, word, freq, dup_or_value = \
                re.split(r'"*\t"*', line.strip('"'))
        # sort и dup_or_value нам не нужны
        item = (lex, pos, flextype, gram, word, freq)
        data.append(item)
    return data


POKRYTIE = '\u0311'
ac2p_conversions = (
    ('\u0131', '\u0456'),  # i без точки в кириллическую десятичную и
    ('[ѧꙗ]', 'я'),  # \u0467 \ua657
    ('[ꙋѹ]', 'у'),  # \ua64b \u0479
    ('~', '\u0483'),
    ("['`]", '\u0301'),
    (r'\^', '\u0302'),
    ('([А-Я])', '\1' + POKRYTIE),  # NOTE: понижение регистра будет выполняться
    # отдельно, см. relwr
)

p2ac_conversions = (
    ('^е', 'є'),
    ('^о', 'ѻ'),
    ('^у', 'ѹ'),
    ('у', 'ꙋ'),
    ('^я', 'ꙗ'),
    ('я', 'ѧ'),
    ('ѡт', 'ѿ'),
    ('\u0483', '~'),
    ('\u0301$', "`"),
    ('\u0301', "'"),
    ('\u0302', '^'),
)


def ac2p(word):
    ''' Antconc to Polyakov's orthography conversion '''
    if word[1:].isupper():
        word = word.lower()
    for src, dst in ac2p_conversions:
        word = re.sub(src, dst, word)
    word = word.lower()  # NOTE:relwr
    return word


def p2ac(word):
    for src, dst in p2ac_conversions:
        word = re.sub(src, dst, word)
    if POKRYTIE in word:
        ix = word.index(POKRYTIE)
        word = word[:ix-1] + word[ix-1:ix].upper() + word[ix+1:]
    return word


class Word:
    def __init__(self, word):
        self._word = word
        self.grams = []

    @property
    def word(self):
        return p2ac(self._word)

    def __str__(self):
        return self.word

    def __repr__(self):
        return repr(self.word)


class Gram:
    def __init__(self, gram, freq, word, lex):
        self.gram = gram
        self.freq = freq
        self.word = word
        self.lex = lex


class Lexeme:
    def __init__(self, lex, pos, flextype, gram):
        self._lex = lex
        self.pos = pos
        self.flextype = flextype
        self.is_graph_num = pos == 'NUM' and not flextype and not gram

    @property
    def lex(self):
        return p2ac(self._lex)

    def __str__(self):
        return self.lex

    def __repr__(self):
        return repr(self.lex)

    def __lt__(self, other):
        return civilrus_convert(self.lex) < civilrus_convert(other.lex)


class Lemmatizer:
    def __init__(self):
        self.lexemes = {}
        self.words = {}

    def add_data(self, data):
        for item in data:
            lex, pos, flextype, gram, word, freq = item
            if word not in self.words:
                self.words[word] = Word(word)

            word_without_titles = ac2p(resolve_titles(p2ac(word)))
            if word_without_titles not in self.words:
                self.words[word_without_titles] = Word(word_without_titles)

            wordform_query = antconc_wordform_query(resolve_titles(p2ac(word)))
            if wordform_query not in self.words:
                self.words[wordform_query] = Word(wordform_query)

            if (lex, pos, flextype) not in self.lexemes:
                self.lexemes[(lex, pos, flextype)] = \
                        Lexeme(lex, pos, flextype, gram)

            L = self.lexemes[(lex, pos, flextype)]
            Ws = [self.words[w] for w in (word, word_without_titles,
                                          wordform_query)]

            for W in Ws:
                W.grams.append(Gram(gram, freq, W, L))

    def _find_lexemes(self, p_word):
        if p_word in self.words:
            _lexemes = list(set(g.lex for g in self.words[p_word].grams))
            lexemes = []
            for lex in _lexemes:
                if '+' in lex.lex or '#' in lex.lex:
                    lexemes.extend(self._find_lexemes(lex.lex) or [])
                else:
                    lexemes.append(lex)
            return list(set(lexemes)) or None

    def find_lexemes(self, ac_word):
        p_word = ac2p(ac_word)
        return self._find_lexemes(p_word)

    def find_other_lexemes(self, lexemes):
        other_lexemes = []
        for lex in self.lexemes.values():
            if lex in lexemes or lex.is_graph_num:
                continue
            other_lexemes.append(lex)
        return other_lexemes


def load_words(*filenames):
    register = {}
    for filename in filenames:
        filepath = os.path.join(path, filename)
        with open(filepath) as f:
            for i, line in enumerate(f.readlines()):
                if i < 3:
                    continue  # В первых трех строках ненужная нам статистика
                freq, word = line.split('\t')[1:3]
                word = word[:1].lower() + word[1:]
                freq = int(freq)
                if word in register:
                    register[word] += freq
                else:
                    register[word] = freq
    return register


def lemmatize_corpus(corpus):
    lemmas = set()
    orphan_words = set()
    for word in corpus:
        lexemes = lem.find_lexemes(word)
        if lexemes is None:
            lexemes = lem.find_lexemes(resolve_titles(word))
        if lexemes is None:
            lexemes = lem._find_lexemes(antconc_wordform_query(word))
        if lexemes is not None:
            for lex in lexemes:
                if lex.is_graph_num or lex in lemmas:
                    continue
                lemmas.add(lex)
        if lexemes is None:
            orphan_words.add(word)
    return lemmas, orphan_words


def get_lemmas_merged_with_bible(lemmas, bible_lemmas):
    chosen = set()
    poss = set()
    for lex in bible_lemmas:
        if lex not in lemmas and re.findall(r'\b(persn|topn|poss)\b', lex.pos):
            if re.findall(r'\bposs\b', lex.pos):
                poss.add(lex)
            continue
        chosen.add(lex)
    return lemmas.union(chosen), poss


def write_collection(collection, filename):
    filepath = os.path.join(path, filename)
    with open(filepath, 'w') as f:
        for item in sorted(collection, key=lambda x: civilrus_convert(str(x))):
            f.write(str(item))
            f.write('\n')


lem = Lemmatizer()
for filename in lem_files:
    filepath = os.path.join(path, filename)
    with open(filepath) as f:
        data = load_data(f)
    lem.add_data(data)
words_basic_corpus = load_words(words_basic_corpus_filename)
words_bible_corpus = load_words(words_bible_corpus_filename)
words_basic_with_bible_corpus = load_words(
        words_basic_corpus_filename, words_bible_corpus_filename)

lemmas, orphan_words = lemmatize_corpus(words_basic_corpus)
bible_lemmas, bible_orphan_words = lemmatize_corpus(words_bible_corpus)

orphan_words = orphan_words.union(bible_orphan_words)
lemmas, poss = get_lemmas_merged_with_bible(lemmas, bible_lemmas)

other_lemmas = lem.find_other_lexemes(lemmas)
write_collection(lemmas, 'test_lemmas.txt')
write_collection(other_lemmas, 'test_other_lemmas.txt')
write_collection(poss, 'test_possessive.txt')
write_collection(orphan_words, 'test_orphans.txt')
lines = (
    'Лексем в лемматизаторе: %s' % len(lem.lexemes),
    'Лексем отобрано для словника: %s' % len(lemmas),
    'Лексем вне словника: %s' % len(other_lemmas),
    '',
    'Всего сегментов: %s' % len(words_basic_with_bible_corpus),
    'Нелемматизированных сегментов: %s' % len(orphan_words),
)
print()
with open(os.path.join(path, 'test_stat.txt'), 'w') as f:
    for line in lines:
        print(line)
        f.write(line + '\n')
