from django import forms

from slavdict.dictionary import viewmodels


class BilletImportForm(forms.Form):
    csvfile = forms.FileField()
    def clean(self):
        cleaned_data = self.cleaned_data
        uploaded_file = cleaned_data.get('csvfile')
        if not uploaded_file.name.upper().endswith('.CSV'):
            raise forms.ValidationError('''Выбранный вами файл «%s»,
                                            похоже, не является
                                            CSV-файлом.''' % uploaded_file.name)
        return cleaned_data


AUTHOR_CHOICES = viewmodels.tupleAuthors
CANONNAME_CHOICES = viewmodels.tupleCanonicalName
GENDER_CHOICES = viewmodels.tupleGenders
GREQSORTBASE_CHOICES = viewmodels.tupleGreqSortbase
GREQSTATUS_CHOICES = viewmodels.tupleGreqStatuses
ONYM_CHOICES = viewmodels.tupleOnyms
POS_CHOICES = viewmodels.tuplePos
POSSESSIVE_CHOICES = viewmodels.tuplePossessive
SORTBASE_CHOICES = viewmodels.tupleSortbase
SORTDIR_CHOICES = viewmodels.tupleSortdir
STATUS_CHOICES = viewmodels.tupleStatuses
TANTUM_CHOICES = viewmodels.tupleTantum
VOLUME_CHOICES = viewmodels.tupleVolumes

class FilterEntriesForm(forms.Form):
    additional_info = forms.BooleanField(label='Статьи с примечаниями', required=False)
    author = forms.ChoiceField(choices=AUTHOR_CHOICES, label='Автор', required=False)
    canonical_name = forms.ChoiceField(choices=CANONNAME_CHOICES, label='Канонические имена', required=False)
    collocations = forms.BooleanField(label='Со словосочетаниями', required=False)
    duplicate = forms.BooleanField(label='Статьи-дубликаты', required=False)
    etymology = forms.BooleanField(label='Статьи с этимологией', required=False)
    etymology_sans = forms.BooleanField(label='Статьи без этимологии', required=False)
    find = forms.CharField(required=False, label='Начинается с')
    gender = forms.ChoiceField(choices=GENDER_CHOICES, label='Род', required=False)
    homonym = forms.BooleanField(label='Статьи-омонимы', required=False)
    meaningcontexts = forms.BooleanField(label='С контекстами значения', required=False)
    onym = forms.ChoiceField(choices=ONYM_CHOICES, label='Тип имени собст.', required=False)
    per_se = forms.BooleanField(label='Отображать помимо заголовочных слов сами статьи', required=False)
    pos = forms.ChoiceField(choices=POS_CHOICES, label='Часть речи', required=False)
    possessive = forms.ChoiceField(choices=POSSESSIVE_CHOICES, label='Притяжательность', required=False)
    sortbase = forms.ChoiceField(choices=SORTBASE_CHOICES, required=False)
    sortdir = forms.ChoiceField(choices=SORTDIR_CHOICES, required=False)
    status = forms.ChoiceField(choices=STATUS_CHOICES, label='Статус статьи', required=False)
    tantum = forms.ChoiceField(choices=TANTUM_CHOICES, label='Число', required=False)
    uninflected = forms.BooleanField(label='Неизменяемые сущ. / прил.', required=False)
    variants = forms.BooleanField(label='С вар-ми написания', required=False)
    volume = forms.ChoiceField(choices=VOLUME_CHOICES, label='Том', required=False)
    default_data = {
        'additional_info': False,
        'author': 'all',
        'canonical_name': 'all',
        'collocations': False,
        'duplicate': False,
        'etymology': False,
        'etymology_sans': False,
        'find': '',
        'gender': 'all',
        'homonym': False,
        'meaningcontexts': False,
        'onym': 'all',
        'per_se': False,
        'pos': 'all',
        'possessive': 'all',
        'sortbase': 't',
        'sortdir':  '-',
        'status': 'all',
        'tantum': 'all',
        'uninflected': False,
        'variants': False,
        'volume': 'all',
    }
    default_data_for_hellinists = default_data.copy()
    default_data_for_hellinists.update({
        'sortdir': '+',
        'sortbase': 'alph',
    })

class FilterExamplesForm(forms.Form):
    hwAddress = forms.CharField(required=False, label='Адрес начинается на')
    hwAllExamples = forms.BooleanField(label='Отображать примеры из незаконченных статей', required=False)
    hwAuthor = forms.ChoiceField(choices=AUTHOR_CHOICES, label='Автор статьи')
    hwExample = forms.CharField(required=False, label='Текст иллюстрации')
    hwExamplesIds = forms.CharField(required=False, label='Идентификаторы иллюстраций')
    hwPrfx = forms.CharField(required=False, label='Статья начинается на')
    hwSortbase = forms.ChoiceField(choices=GREQSORTBASE_CHOICES)
    hwSortdir = forms.ChoiceField(choices=SORTDIR_CHOICES, required=False)
    hwStatus = forms.ChoiceField(choices=GREQSTATUS_CHOICES, label='Статус греч. парал.')
    hwVolume = forms.ChoiceField(choices=VOLUME_CHOICES, label='Том')
    default_data = {
        'hwAddress': '',
        'hwAllExamples': False,
        'hwAuthor': 'all',
        'hwExample': '',
        'hwExamplesIds': '',
        'hwPrfx': '',
        'hwSortbase': 'addr',
        'hwSortdir': '+',
        'hwStatus': 'all',
        'hwVolume': 'all',
    }
