import re

from slavdict.dictionary.constants import ENTRY_SPECIAL_CASES
from slavdict.dictionary.constants import GENDER_CHOICES, GENDER_MAP
from slavdict.dictionary.constants import TANTUM_CHOICES, TANTUM_MAP
from slavdict.dictionary.constants import SC1, SC2, SC3, SC4, SC5, SC6, SC7, SC8
from slavdict.dictionary.constants import SC9, SC10
from slavdict.dictionary.utils import ucs_convert as ucs8
from slavdict.jinja_extensions.hyphenation import hyphenate_ucs8 as h
from slavdict.jinja_extensions import trim_spaces as ts

def special_cases_func(self, case):
    RE_COMMA = r'[,\s]+'
    if case == 'several nouns':
        if (self.genitive and ',' in self.genitive and
                len(self.base_vars) > 1 and
                self.special_case and
                self.special_case in ENTRY_SPECIAL_CASES):
            M_GENDER = dict(GENDER_CHOICES)[GENDER_MAP['masculine']]
            F_GENDER = dict(GENDER_CHOICES)[GENDER_MAP['feminine']]
            N_GENDER = dict(GENDER_CHOICES)[GENDER_MAP['neutral']]
            PL_TANTUM = dict(TANTUM_CHOICES)[TANTUM_MAP['pluraleTantum']]
            UNINFL = 'неизм.'
            HIDDEN_GRAM = ''
            HIDDEN_FORM = ''

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
                    '%s %s' % (M_GENDER, UNINFL)]
                wordforms += [HIDDEN_FORM]
            elif SC7 == sc:
                grammatical_marks = [F_GENDER, N_GENDER]
            elif SC8 == sc:
                grammatical_marks = [HIDDEN_GRAM] * 3
                grammatical_marks += [self.get_gender_display()]
                wordforms = [HIDDEN_FORM, wordforms[0], HIDDEN_FORM, wordforms[1]]
            elif SC10 == sc:
                grammatical_marks = [M_GENDER, N_GENDER]

            value = [(wordform, ucs8(wordform), grammatical_marks[i])
                     for i, wordform in enumerate(wordforms)]
            return value
    elif case == 'be' and self.civil_equivalent == 'быти':
        return [ucs8(x) for x in ("нѣ'смь", "нѣ'си")]
    elif case == 'bigger':
        if self.civil_equivalent == 'больший':
            return ucs8("вели'кій")
        elif self.civil_equivalent == 'горший':
            return ucs8("ѕлы'й")

    elif case == 'other_volumes':
        STAR = '\u27e1'
        STAR_CLS = 'MeaningfulNoAccent'
        if 'вриена' == self.civil_equivalent:
            base_vars = tuple(self.base_vars)
            tags = (
                {'text': base_vars[0].idem_ucs, 'class': 'Headword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': self.genitive_ucs_wax[1], 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'ж.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': base_vars[1].idem_ucs, 'class': 'SubHeadword'},
                {'text': ts.SPACE},
                {'text': 'ж.', 'class': 'Em'},
                {'text': ts.EMSPACE},
                {'text': 'неизм.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags

        elif self.civil_equivalent in ('ветреный', 'ветренный'):
            base_vars = tuple(self.base_vars)
            tags = (
                {'text': base_vars[0].idem_ucs, 'class': 'Headword'},
                {'text': ts.SPACE},
                {'text': '(', 'class': 'Text'},
                {'text': base_vars[0].childvars[0].idem_ucs,
                    'class': 'CSLSegment'},
                {'text': '),', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': self.short_form_ucs_wax[1],
                    'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': base_vars[1].idem_ucs, 'class': 'SubHeadword'},
                {'text': ts.SPACE},
                {'text': 'прил.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags

        elif self.civil_equivalent in (
                'воскласти', 'вскласти',  # перех.
                'воскормити', 'вскормити',  # перех.
                'восприимати', 'воспринимати',  # перех. и неперех.
                'воспящати', 'вспящати',  # перех. и неперех.
                'востаяти', 'встаяти'  # неперех.
                ):
            base_vars = tuple(self.base_vars)
            tags = (
                {'text': base_vars[0].idem_ucs, 'class': 'Headword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8(
                    self.several_sg1[0][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg1[0][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )
            tags += (
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8(
                    self.several_sg2[0][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg2[0][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )
            tags += (
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': h(base_vars[1].idem_ucs),
                    'class': 'SubHeadword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8(
                    self.several_sg1[1][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg1[1][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )
            tags += (
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8(
                    self.several_sg2[1][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg2[1][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )
            if self.civil_equivalent in ('востаяти', 'встаяти'):
                tags += (
                    {'text': ts.SPACE},
                    {'text': 'неперех.', 'class': 'Em'},
                    {'text': ts.SPACE},
                )
            else:
                tags += (
                    {'text': ts.SPACE},
                    {'text': 'перех.', 'class': 'Em'},
                    {'text': ts.SPACE},
                )
                if self.civil_equivalent in (
                        'восприимати', 'воспринимати',
                        'воспящати', 'вспящати'):
                    tags += (
                        {'text': 'и', 'class': 'Em'},
                        {'text': ts.SPACE},
                        {'text': 'неперех.', 'class': 'Em'},
                        {'text': ts.SPACE},
                    )
            return tags

        elif self.civil_equivalent in ('взяти', 'взятися'):
            base_vars = tuple(self.base_vars)
            tags = (
                {'text': base_vars[0].idem_ucs, 'class': 'Headword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8(
                    self.several_sg1[0][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg1[0][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )
            tags += (
                {'text': ts.SPACE},
                {'text': '(', 'class': 'Text'},
                {'text': h(ucs8(
                    self.several_sg1[1][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg1[1][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )

            tags += (
                {'text': '),', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8(
                    self.several_sg2[0][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg2[0][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )
            tags += (
                {'text': ts.SPACE},
                {'text': '(', 'class': 'Text'},
                {'text': h(ucs8(
                    self.several_sg2[1][0])), 'class': 'CSLSegment'},
            )
            if ts.has_no_accent(self.several_sg2[1][0]):
                tags += (
                    {'text': STAR, 'class': STAR_CLS},
                )
            tags += (
                {'text': ')', 'class': 'Text'},
                {'text': ts.SPACE},
            )
            if self.civil_equivalent == 'взяти':
                tags += (
                    {'text': 'перех.', 'class': 'Em'},
                    {'text': ts.SPACE},
                    {'text': 'и', 'class': 'Em'},
                    {'text': ts.SPACE},
                    {'text': 'неперех.', 'class': 'Em'},
                    {'text': ts.SPACE},
                )
            elif self.civil_equivalent == 'взятися':
                tags += (
                    {'text': 'неперех.', 'class': 'Em'},
                    {'text': ts.SPACE},
                )
            return tags

        elif self.civil_equivalent == 'воздвигнути':
            forms = tuple(self.base_vars)
            sg1_segs = [
                (h(ucs_word), STAR) if ts.has_no_accent(word)
                else (h(ucs_word),)
                for word, ucs_word in self.several_sg1]
            sg1_clss = [
                ('CSLSegment', STAR_CLS) if ts.has_no_accent(word)
                else ('CSLSegment',)
                for word, ucs_word in self.several_sg1]
            sg2_segs = [
                (h(ucs_word), STAR) if ts.has_no_accent(word)
                else (h(ucs_word),)
                for word, ucs_word in self.several_sg2]
            sg2_clss = [
                ('CSLSegment', STAR_CLS) if ts.has_no_accent(word)
                else ('CSLSegment',)
                for word, ucs_word in self.several_sg2]
            segs = (forms[0].idem_ucs, ',', ts.SPACE)
            clss = ('Headword', 'Text', None)
            segs += sg1_segs[0]
            clss += sg1_clss[0]
            segs += (ts.SPACE, 'и', ts.SPACE)
            clss += (None, 'Conj', None)
            segs += sg1_segs[1]
            clss += sg1_clss[1]
            segs += (',', ts.SPACE)
            clss += ('Text', None)
            segs += sg2_segs[0]
            clss += sg2_clss[0]
            segs += (ts.SPACE, 'и', ts.SPACE)
            clss += (None, 'Conj', None)
            segs += sg2_segs[1]
            clss += sg2_clss[1]

            segs += (ts.SPACE, 'и', ts.SPACE)
            clss += (None, 'Conj', None)
            segs += (h(forms[1].idem_ucs), ',', ts.SPACE)
            clss += ('SubHeadword', 'Text', None)
            segs += sg1_segs[2]
            clss += sg1_clss[2]
            segs += (',', ts.SPACE)
            clss += ('Text', None)
            segs += sg2_segs[2]
            clss += sg2_clss[2]
            segs += (ts.SPACE, 'перех.', ts.SPACE)
            clss += (None, 'Em', None)

            tags = []
            for seg, cls in zip(segs, clss):
                tag = {'text': seg}
                if cls:
                    tag['class'] = cls
                tags.append(tag)
            return tags

        elif self.civil_equivalent in ('владычний', 'владычный'):
            forms = tuple(self.base_vars)
            short_form_segs = [
                (h(ucs_word), STAR) if ts.has_no_accent(word)
                else (h(ucs_word),)
                for word, ucs_word in self.short_forms]
            short_form_clss = [
                ('CSLSegment', STAR_CLS) if ts.has_no_accent(word)
                else ('CSLSegment',)
                for word, ucs_word in self.short_forms]
            segs = (forms[0].idem_ucs, ts.SPACE, '(')
            clss = ('Headword', None, 'Text')
            segs += (h(forms[0].childvars[0].idem_ucs), ',', ts.SPACE)
            clss += ('CSLSegment', 'Text', None)
            segs += (h(forms[0].idem_ucs), '),', ts.SPACE)
            clss += ('CSLSegment', 'Text', None)
            segs += short_form_segs[0]
            clss += short_form_clss[0]

            segs += (ts.SPACE, 'и', ts.SPACE)
            clss += (None, 'Conj', None)
            segs += (forms[1].idem_ucs, ts.SPACE, '(')
            clss += ('SubHeadword', None, 'Text')
            segs += (h(forms[1].childvars[0].idem_ucs), ',', ts.SPACE)
            clss += ('CSLSegment', 'Text', None)
            segs += (h(forms[1].idem_ucs), '),', ts.SPACE)
            clss += ('CSLSegment', 'Text', None)
            segs += short_form_segs[1]
            clss += short_form_clss[1]

            segs += (ts.SPACE, 'прил. притяж.', ts.SPACE)
            clss += (None, 'Em', None)

            tags = []
            for seg, cls in zip(segs, clss):
                tag = {'text': seg}
                if cls:
                    tag['class'] = cls
                tags.append(tag)
            return tags

        elif self.civil_equivalent in ('галгалы', 'галгал', 'галгала'):
            tags = (
                {'text': ucs8("галга'лы"), 'class': 'Headword'},
                {'text': ts.SPACE},
                {'text': '(', 'class': 'Text'},
                {'text': h(ucs8("галга^лы")), 'class': 'CSLSegment'},
                {'text': '),', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8("галга'лъ")), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'только мн.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': h(ucs8("галга'лъ")), 'class': 'SubHeadword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8("галга'ла")), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'м.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': h(ucs8("галга'ла")), 'class': 'SubHeadword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8("галга'лы")), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'ж.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags

        elif self.civil_equivalent in ('гангрянин', 'гаггрянин',
                                       'гангряне', 'гаггряне'):
            tags = (
                {'text': ucs8("га'нгрѧнинъ"), 'class': 'Headword'},
                {'text': ts.SPACE},
                {'text': '(', 'class': 'Text'},
                {'text': h(ucs8("га'ггрѧнинъ")), 'class': 'CSLSegment'},
                {'text': '),', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': ucs8("га'нгрѧнина"), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'м.', 'class': 'Em'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': ucs8("га'нгрѧне"), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': '(', 'class': 'Text'},
                {'text': ucs8("га'ггрѧне"), 'class': 'CSLSegment'},
                {'text': ')', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': 'мн.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags

        elif self.civil_equivalent in ('гефсимани', 'гефсиманиа'):
            base_vars = tuple(self.base_vars)
            tags = (
                {'text': base_vars[0].idem_ucs, 'class': 'Headword'},
                {'text': ts.SPACE},
                {'text': '(', 'class': 'Text'},
                {'text': h(ucs8("геѳсима'ніа")), 'class': 'CSLSegment'},
                {'text': '),', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': self.genitive_ucs_wax[1], 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'ж.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': base_vars[1].idem_ucs, 'class': 'SubHeadword'},
                {'text': ts.SPACE},
                {'text': 'неизм.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags

        elif self.civil_equivalent in ('епитрахиль', 'епитрахилий'):
            base_vars = tuple(self.base_vars)
            genitives = self.genitives
            tags = (
                {'text': base_vars[0].idem_ucs, 'class': 'Headword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': genitives[0][1], 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'м.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': genitives[1][1], 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'ж.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': base_vars[1].idem_ucs, 'class': 'SubHeadword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': genitives[2][1], 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'м.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags

        elif self.civil_equivalent in ('епомис', 'епомида'):
            tags = (
                {'text': ucs8("єпѡмі'да"), 'class': 'Headword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8("єпѡмі'ды")), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'ж.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': ucs8("єпѡмі'съ"), 'class': 'SubHeadword'},
                {'text': ts.SPACE},
                {'text': 'неизм.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags

        elif self.civil_equivalent in ('ехидна', 'ехидн'):
            tags = (
                {'text': ucs8("єхі'дна"), 'class': 'Headword'},
                {'text': ',', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': ucs8("єхі'дны"), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'ж.', 'class': 'Em'},
                {'text': ts.SPACE},
                {'text': 'и', 'class': 'Conj'},
                {'text': ts.SPACE},
                {'text': ucs8("єхі'днъ"), 'class': 'SubHeadword'},
                {'text': '(?),', 'class': 'Text'},
                {'text': ts.SPACE},
                {'text': h(ucs8("єхі'дна")), 'class': 'CSLSegment'},
                {'text': ts.SPACE},
                {'text': 'м.', 'class': 'Em'},
                {'text': ts.SPACE},
            )
            return tags
