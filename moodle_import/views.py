# -*- coding: utf-8 -*-

from dictionary.forms import BilletImportForm
from django.http import HttpResponse, HttpResponseRedirect
import slavdict.unicode_csv as unicode_csv
import StringIO

from custom_user.models import CustomUser
from slavdict.directory.models import CategoryValue
ccc = CategoryValue.objects.get(pk=46) # Импортирована (Статус статьи "Статья импортирована из Moodle")

from slavdict.dictionary.models import entry_dict, civilrus_convert
from slavdict.dictionary.models import Entry, OrthographicVariant, Meaning, Example, CollocationGroup


orthvars = []

csv_columns = {
    u'Заглавное слово': '',
    u'Отсылка': '',
    u'Орфографический вариант (1)': '',
    u'Орфографический вариант (2)': '',
    u'Орфографический вариант (3)': '',
    u'Орфографический вариант (4)': '',
    u'Часть речи': '',
    u'Словоформы': '',
    u'1 лицо': '',
    u'2 лицо': '',
    u'Р. падеж': '',
    u'Род': '',
    u'Число': '',
    u'Разряд по значению': '',
    u'Неизменяемость': '',
    u'Значение слова (1)': '',
    u'Значение слова (2)': '',
    u'Значение слова (3)': '',
    u'Значение слова (4)': '',
    u'Значение слова (5)': '',
    u'Пример для значения 1 (1)': '',
    u'Пример для значения 1 (2)': '',
    u'Пример для значения 1 (3)': '',
    u'Пример для значения 2 (1)': '',
    u'Пример для значения 2 (2)': '',
    u'Пример для значения 2 (3)': '',
    u'Пример для значения 3 (1)': '',
    u'Пример для значения 3 (2)': '',
    u'Пример для значения 3 (3)': '',
    u'Пример для значения 4 (1)': '',
    u'Пример для значения 4 (2)': '',
    u'Пример для значения 4 (3)': '',
    u'Пример для значения 5 (1)': '',
    u'Пример для значения 5 (2)': '',
    u'Пример для значения 5 (3)': '',
    u'Адрес для примера 1.1': '',
    u'Адрес для примера 1.2': '',
    u'Адрес для примера 1.3': '',
    u'Адрес для примера 2.1': '',
    u'Адрес для примера 2.2': '',
    u'Адрес для примера 2.3': '',
    u'Адрес для примера 3.1': '',
    u'Адрес для примера 3.2': '',
    u'Адрес для примера 3.3': '',
    u'Адрес для примера 4.1': '',
    u'Адрес для примера 4.2': '',
    u'Адрес для примера 4.3': '',
    u'Адрес для примера 5.1': '',
    u'Адрес для примера 5.2': '',
    u'Адрес для примера 5.3': '',
    u'Автор статьи': '',
    u'Запрос для AntConc': '',
    u'Греч. параллель для слав. слов': '',
    u'Виза редактора': '',
    u'Статус': '',
    u'Реконструкция': '',
    u'Наличие запроса для AntConc': '',
    u'Комментарий редактора': '',
    u'Свободное поле': '',
    u'Наличие замечаний редактора': '',
    u'Надежность реконструкции': '',
    u'Контекст 1.1': '',
    u'Контекст 1.2': '',
    u'И.ед. для ‘тот или иной народ’': '',
    u'Краткая форма': '',
    u'Имя собственное': '',
    u'Метафорическое употребление (1)': '',
    u'Устойчивое сочетание (3)': '',
    u'Устойчивое сочетание (1)': '',
    u'Устойчивое сочетание (2)': '',
    u'Греч. параллель': '',
    u'Контекст 1.3': '',
    u'Греч. параллель для контекста 1.1': '',
    u'Греч. параллель для контекста 1.2': '',
    u'Греч. параллель для контекста 1.3': '',
    u'Метафорическое употребление (2)': '',
    u'Метафорическое употребление (3)': '',
    u'Пример для метафоры 1.1': '',
    u'Пример для метафоры 1.2': '',
    u'Пример для метафоры 1.3': '',
    u'Пример для метафоры 2.1': '',
    u'Пример для метафоры 2.2': '',
    u'Пример для метафоры 2.3': '',
    u'Пример для метафоры 3.1': '',
    u'Пример для метафоры 3.2': '',
    u'Пример для метафоры 3.3': '',
    u'Адрес для примера метафоры 1.1': '',
    u'Адрес для примера метафоры 1.2': '',
    u'Адрес для примера метафоры 1.3': '',
    u'Адрес для примера метафоры 2.1': '',
    u'Адрес для примера метафоры 2.2': '',
    u'Адрес для примера метафоры 2.3': '',
    u'Адрес для примера метафоры 3.1': '',
    u'Адрес для примера метафоры 3.2': '',
    u'Адрес для примера метафоры 3.3': '',
    u'Наличие греч. параллелей для контекстов': '',
    u'Толкование слова (1)': '',
    u'Толкование слова (2)': '',
    u'Толкование слова (3)': '',
    u'Толкование слова (4)': '',
    u'Толкование слова (5)': '',
    u'Контекст 2.1': '',
    u'Контекст 2.2': '',
    u'Контекст 2.3': '',
    u'Контекст 3.1': '',
    u'Контекст 3.2': '',
    u'Контекст 3.3': '',
    u'Контекст 4.1': '',
    u'Контекст 4.2': '',
    u'Контекст 4.3': '',
    u'Контекст 5.1': '',
    u'Контекст 5.2': '',
    u'Контекст 5.3': '',
    u'Греч. параллель для контекста 2.1': '',
    u'Греч. параллель для контекста 2.2': '',
    u'Греч. параллель для контекста 2.3': '',
    u'Греч. параллель для контекста 3.1': '',
    u'Греч. параллель для контекста 3.2': '',
    u'Греч. параллель для контекста 3.3': '',
    u'Греч. параллель для контекста 4.1': '',
    u'Греч. параллель для контекста 4.2': '',
    u'Греч. параллель для контекста 4.3': '',
    u'Греч. параллель для контекста 5.1': '',
    u'Греч. параллель для контекста 5.2': '',
    u'Греч. параллель для контекста 5.3': '',
    u'Частотность': '',
    u'Контекст для метафоры 1.1': '',
    u'Контекст для метафоры 1.2': '',
    u'Контекст для метафоры 1.3': '',
    u'Контекст для метафоры 2.1': '',
    u'Контекст для метафоры 2.2': '',
    u'Контекст для метафоры 2.3': '',
    u'Контекст для метафоры 3.1': '',
    u'Контекст для метафоры 3.2': '',
    u'Контекст для метафоры 3.3': '',
    u'Греч. параллель для метафоры 1.1': '',
    u'Греч. параллель для метафоры 1.2': '',
    u'Греч. параллель для метафоры 1.3': '',
    u'Греч. параллель для метафоры 2.1': '',
    u'Греч. параллель для метафоры 2.2': '',
    u'Греч. параллель для метафоры 2.3': '',
    u'Греч. параллель для метафоры 3.1': '',
    u'Греч. параллель для метафоры 3.2': '',
    u'Греч. параллель для метафоры 3.3': '',
    u'Пример для значения 1 (4)': '',
    u'Пример для значения 1 (5)': '',
    u'Пример для значения 1 (6)': '',
    u'Пример для значения 1 (7)': '',
    u'Пример для значения 1 (8)': '',
    u'Адрес для примера 1.4': '',
    u'Адрес для примера 1.5': '',
    u'Адрес для примера 1.6': '',
    u'Адрес для примера 1.7': '',
    u'Адрес для примера 1.8': '',
    u'Греч. параллель для контекста 1.4': '',
    u'Греч. параллель для контекста 1.5': '',
    u'Греч. параллель для контекста 1.6': '',
    u'Греч. параллель для контекста 1.7': '',
    u'Греч. параллель для контекста 1.8': '',
    u'Контекст 1.4': '',
    u'Контекст 1.5': '',
    u'Контекст 1.6': '',
    u'Контекст 1.7': '',
    u'Контекст 1.8': '',
    u'Пример для значения 2 (4)': '',
    u'Адрес для примера 2.4': '',
    u'Контекст 2.4': '',
    u'Греч. параллель для контекста 2.4': '',
    u'Статус параллелей': '',
    u'Номер для словарных статей омонимов': '',
    u'Пояснение для словарных статей омонимов': '',
    u'Реконструкция орф. вар. (1)': '',
    u'Реконструкция орф. вар. (2)': '',
    u'Реконструкция орф. вар. (3)': '',
    u'Реконструкция орф. вар. (4)': '',
}

csv_translate = {
    'headword': u'Заглавное слово',
    'orthvar1': u'Орфографический вариант (1)',
    'orthvar2': u'Орфографический вариант (2)',
    'orthvar3': u'Орфографический вариант (3)',
    'orthvar4': u'Орфографический вариант (4)',
    
    'reconstr': u'Реконструкция',
    'reconstr_ov1': u'Реконструкция орф. вар. (1)',
    'reconstr_ov2': u'Реконструкция орф. вар. (2)',
    'reconstr_ov3': u'Реконструкция орф. вар. (3)',
    'reconstr_ov4': u'Реконструкция орф. вар. (4)',

    'reconstr_reliability': u'Надежность реконструкции', # игнорируем
    'frequency': u'Частотность', # игнорируем


    'hom_num': u'Номер для словарных статей омонимов',
    'hom_gloss': u'Пояснение для словарных статей омонимов',

    'antconc': u'Запрос для AntConc',
    'antconc_bool': u'Наличие запроса для AntConc', # игнорируем
    'wordforms': u'Словоформы',

    'author': u'Автор статьи',
    'visa': u'Виза редактора', # игнорируем
    'status': u'Статус',
    'edcomment': u'Комментарий редактора', # игнорируем
    'edcomment_bool': u'Наличие замечаний редактора', # игнорируем
    'grequiv_status_bool': u'Наличие греч. параллелей для контекстов', # игнорируем
    'grequiv_status': u'Статус параллелей',  # игнорируем

    'free': u'Свободное поле',

    'entry_sm': u'Отсылка',



    'pos': u'Часть речи',
    '1sg': u'1 лицо',
    '2sg': u'2 лицо',
    'Gen': u'Р. падеж',
    'NomSg': u'И.ед. для ‘тот или иной народ’',
    'gender': u'Род',
    'number': u'Число',
    'proper_name_type': u'Разряд по значению',
    'uninflected': u'Неизменяемость',
    'short_form': u'Краткая форма',
    'proper_name': u'Имя собственное',


    'etym': u'Греч. параллель',
    'etym0': u'Греч. параллель для слав. слов', # игнорируем

    

    'm1': u'Значение слова (1)',
    'm2': u'Значение слова (2)',
    'm3': u'Значение слова (3)',
    'm4': u'Значение слова (4)',
    'm5': u'Значение слова (5)',

    'gl1': u'Толкование слова (1)',
    'gl2': u'Толкование слова (2)',
    'gl3': u'Толкование слова (3)',
    'gl4': u'Толкование слова (4)',
    'gl5': u'Толкование слова (5)',


    'm1ex1': u'Пример для значения 1 (1)',
    'm1ex2': u'Пример для значения 1 (2)',
    'm1ex3': u'Пример для значения 1 (3)',
    'm1ex4': u'Пример для значения 1 (4)',
    'm1ex5': u'Пример для значения 1 (5)',
    'm1ex6': u'Пример для значения 1 (6)',
    'm1ex7': u'Пример для значения 1 (7)',
    'm1ex8': u'Пример для значения 1 (8)',

    'm2ex1': u'Пример для значения 2 (1)',
    'm2ex2': u'Пример для значения 2 (2)',
    'm2ex3': u'Пример для значения 2 (3)',
    'm2ex4': u'Пример для значения 2 (4)',

    'm3ex1': u'Пример для значения 3 (1)',
    'm3ex2': u'Пример для значения 3 (2)',
    'm3ex3': u'Пример для значения 3 (3)',
    'm4ex1': u'Пример для значения 4 (1)',
    'm4ex2': u'Пример для значения 4 (2)',
    'm4ex3': u'Пример для значения 4 (3)',
    'm5ex1': u'Пример для значения 5 (1)',
    'm5ex2': u'Пример для значения 5 (2)',
    'm5ex3': u'Пример для значения 5 (3)',


    'm1adr1': u'Адрес для примера 1.1',
    'm1adr2': u'Адрес для примера 1.2',
    'm1adr3': u'Адрес для примера 1.3',
    'm1adr4': u'Адрес для примера 1.4',
    'm1adr5': u'Адрес для примера 1.5',
    'm1adr6': u'Адрес для примера 1.6',
    'm1adr7': u'Адрес для примера 1.7',
    'm1adr8': u'Адрес для примера 1.8',

    'm2adr1': u'Адрес для примера 2.1',
    'm2adr2': u'Адрес для примера 2.2',
    'm2adr3': u'Адрес для примера 2.3',
    'm2adr4': u'Адрес для примера 2.4',

    'm3adr1': u'Адрес для примера 3.1',
    'm3adr2': u'Адрес для примера 3.2',
    'm3adr3': u'Адрес для примера 3.3',
    'm4adr1': u'Адрес для примера 4.1',
    'm4adr2': u'Адрес для примера 4.2',
    'm4adr3': u'Адрес для примера 4.3',
    'm5adr1': u'Адрес для примера 5.1',
    'm5adr2': u'Адрес для примера 5.2',
    'm5adr3': u'Адрес для примера 5.3',


    'm1ctxt1': u'Контекст 1.1',
    'm1ctxt2': u'Контекст 1.2',
    'm1ctxt3': u'Контекст 1.3',
    'm1ctxt4': u'Контекст 1.4',
    'm1ctxt5': u'Контекст 1.5',
    'm1ctxt6': u'Контекст 1.6',
    'm1ctxt7': u'Контекст 1.7',
    'm1ctxt8': u'Контекст 1.8',

    'm2ctxt1': u'Контекст 2.1',
    'm2ctxt2': u'Контекст 2.2',
    'm2ctxt3': u'Контекст 2.3',
    'm2ctxt4': u'Контекст 2.4',

    'm3ctxt1': u'Контекст 3.1',
    'm3ctxt2': u'Контекст 3.2',
    'm3ctxt3': u'Контекст 3.3',
    'm4ctxt1': u'Контекст 4.1',
    'm4ctxt2': u'Контекст 4.2',
    'm4ctxt3': u'Контекст 4.3',
    'm5ctxt1': u'Контекст 5.1',
    'm5ctxt2': u'Контекст 5.2',
    'm5ctxt3': u'Контекст 5.3',


    'm1gr1': u'Греч. параллель для контекста 1.1',
    'm1gr2': u'Греч. параллель для контекста 1.2',
    'm1gr3': u'Греч. параллель для контекста 1.3',
    'm1gr4': u'Греч. параллель для контекста 1.4',
    'm1gr5': u'Греч. параллель для контекста 1.5',
    'm1gr6': u'Греч. параллель для контекста 1.6',
    'm1gr7': u'Греч. параллель для контекста 1.7',
    'm1gr8': u'Греч. параллель для контекста 1.8',

    'm2gr1': u'Греч. параллель для контекста 2.1',
    'm2gr2': u'Греч. параллель для контекста 2.2',
    'm2gr3': u'Греч. параллель для контекста 2.3',
    'm2gr4': u'Греч. параллель для контекста 2.4',

    'm3gr1': u'Греч. параллель для контекста 3.1',
    'm3gr2': u'Греч. параллель для контекста 3.2',
    'm3gr3': u'Греч. параллель для контекста 3.3',
    'm4gr1': u'Греч. параллель для контекста 4.1',
    'm4gr2': u'Греч. параллель для контекста 4.2',
    'm4gr3': u'Греч. параллель для контекста 4.3',
    'm5gr1': u'Греч. параллель для контекста 5.1',
    'm5gr2': u'Греч. параллель для контекста 5.2',
    'm5gr3': u'Греч. параллель для контекста 5.3',



    'mm1': u'Метафорическое употребление (1)',
    'mm2': u'Метафорическое употребление (2)',
    'mm3': u'Метафорическое употребление (3)',

    'mm1ex1': u'Пример для метафоры 1.1',
    'mm1ex2': u'Пример для метафоры 1.2',
    'mm1ex3': u'Пример для метафоры 1.3',
    'mm2ex1': u'Пример для метафоры 2.1',
    'mm2ex2': u'Пример для метафоры 2.2',
    'mm2ex3': u'Пример для метафоры 2.3',
    'mm3ex1': u'Пример для метафоры 3.1',
    'mm3ex2': u'Пример для метафоры 3.2',
    'mm3ex3': u'Пример для метафоры 3.3',

    'mm1adr1': u'Адрес для примера метафоры 1.1',
    'mm1adr2': u'Адрес для примера метафоры 1.2',
    'mm1adr3': u'Адрес для примера метафоры 1.3',
    'mm2adr1': u'Адрес для примера метафоры 2.1',
    'mm2adr2': u'Адрес для примера метафоры 2.2',
    'mm2adr3': u'Адрес для примера метафоры 2.3',
    'mm3adr1': u'Адрес для примера метафоры 3.1',
    'mm3adr2': u'Адрес для примера метафоры 3.2',
    'mm3adr3': u'Адрес для примера метафоры 3.3',


    'mm1ctxt1': u'Контекст для метафоры 1.1',
    'mm1ctxt2': u'Контекст для метафоры 1.2',
    'mm1ctxt3': u'Контекст для метафоры 1.3',
    'mm2ctxt1': u'Контекст для метафоры 2.1',
    'mm2ctxt2': u'Контекст для метафоры 2.2',
    'mm2ctxt3': u'Контекст для метафоры 2.3',
    'mm3ctxt1': u'Контекст для метафоры 3.1',
    'mm3ctxt2': u'Контекст для метафоры 3.2',
    'mm3ctxt3': u'Контекст для метафоры 3.3',

    'mm1gr1': u'Греч. параллель для метафоры 1.1',
    'mm1gr2': u'Греч. параллель для метафоры 1.2',
    'mm1gr3': u'Греч. параллель для метафоры 1.3',
    'mm2gr1': u'Греч. параллель для метафоры 2.1',
    'mm2gr2': u'Греч. параллель для метафоры 2.2',
    'mm2gr3': u'Греч. параллель для метафоры 2.3',
    'mm3gr1': u'Греч. параллель для метафоры 3.1',
    'mm3gr2': u'Греч. параллель для метафоры 3.2',
    'mm3gr3': u'Греч. параллель для метафоры 3.3',


    'cg1': u'Устойчивое сочетание (1)',
    'cg2': u'Устойчивое сочетание (2)',
    'cg3': u'Устойчивое сочетание (3)',
}

# Вспомогательные функции и классы
def g(column_name):
    return csv_columns[csv_translate[column_name]]

class MoodleEntry:
    def __init__(self):
        self.orthvars = []

def get_bool(x):
    if x==u'да':
        return True
    elif x==u'нет' or not x:
        return False
    else:
        raise NameError(u"Булевское поле заполнено неправильно.")

# Основная view-функция
@login_required
def import_moodle_base(request):

    if request.method == 'POST':
        form = BilletImportForm(request.POST, request.FILES)
        if form.is_valid():

            csvfile = request.FILES['csvfile']
            csv_reader = unicode_csv.UnicodeReader(csvfile, dialect=unicode_csv.calc, encoding='utf-8')

            output = StringIO.StringIO()
            csv_writer = unicode_csv.UnicodeWriter(output, dialect=unicode_csv.calc, encoding='utf-8')

            headers = csv_reader.next()
            csv_writer.writerow(headers)
            for n, column_name in enumerate(headers):
                column_name = column_name.strip()
                if column_name not in csv_columns:
                    raise NameError(u'Не учтённое название столбца в CSV-файле.')
                csv_columns[column_name] = n

            idems = OrthographicVariant.objects.all().values_list('idem') # Список списков, каждый из которых содержит один элемент.
            idems = [x[0] for x in idems] # Переходим от списка списков к списку самих элементов (орфографических вариантов).
            authors = CustomUser.objects.all()

            orthvar_collisions = False
            csv_authors = {}

            for row in csv_reader:
                ENTRY = MoodleEntry()
                L1 = ('headword', 'orthvar1', 'orthvar2', 'orthvar3', 'orthvar4')
                L1 = [row[g(i)].strip() for i in L1]
                L2 = ('reconstr', 'reconstr_ov1', 'reconstr_ov2', 'reconstr_ov3', 'reconstr_ov4')
                L2 = [get_bool(row[g(i)].strip()) for i in L2]
                ENTRY.orthvars = [OrthographicVariant(idem=i, is_reconstructed=j) for i, j in zip(L1, L2) if i]

                for orthvar in ENTRY.orthvars:
                    if orthvar.idem in idems:
                        orthvar_collisions = True
                        csv_writer.writerow(row)
                        break
                else:
                    author_in_csv = row[g('author')]
                    # Проверяем нет ли автора в кэше, т.е. не находили ли мы его уже раньше
                    if author_in_csv in csv_authors:
                        author = csv_authors[author_in_csv]
                    # если мы его раньше не находили, то находим
                    else:
                        for au in authors:
                            if au.last_name and author_in_csv.startswith(au.last_name):
                                author = au
                                csv_authors[author_in_csv] = au
                                break
                        else:
                            raise NameError(u"Автор, указанный в CSV-файле, не найден среди участников работы над словарём.")

                    entry_args = entry_dict.copy() # Поверхностная (!) копия словаря.

                    # Номер омонима
                    hom_num = row[g('hom_num')]
                    if hom_num:
                        hom_num = int(hom_num)
                    else:
                        hom_num = None

                    # Свободное поле и поле ссылки
                    additional_info = row[g('free')]
                    entry_sm = row[g('entry_sm')]
                    if entry_sm:
                        additional_info = u'%s || см. %s' % (additional_info, entry_sm) if additional_info else u'см. %s' % entry_sm

                    #Часть речи
                    pos = row[g('pos')].strip()
                    posL = CategoryValue.objects.filter(category__slug='partOfSpeech')
                    if pos:
                        for p in posL:
                            if pos==p.tag:
                                pos = p
                                break
                        else:
                            raise NameError(u'Ярлык части речи не опознан.')
                    else:
                        pos = None

                    # Грамматический род
                    gender = row[g('gender')].strip()
                    genderL = CategoryValue.objects.filter(category__slug='gender')
                    if gender:
                        for g in genderL:
                            if gender==g.tag:
                                gender = g
                                break
                        else:
                            raise NameError(u'Ярлык грамматического рода не опознан.')
                    else:
                        gender = None

                    # Число (tantum)
                    tantum = row[g('number')].strip()
                    tantumL = CategoryValue.objects.filter(category__slug='tantum')
                    if tantum:
                        for t in tantumL:
                            if tantum==t.tag:
                                tantum = t
                                break
                        else:
                            raise NameError(u'Ярлык числа не опознан.')
                    else:
                        tantum = None

                    # Имя собственное
                    onymB = get_bool(row[g('proper_name')]).strip()
                    onym = row[g('proper_name_type')].strip()
                    onymL = CategoryValue.objects.filter(category__slug='onym')
                    onymOTH = onymL.get(tag=u'другое')
                    if onym:
                        for o in onymL:
                            if onym==o.tag:
                                onym = o
                                break
                        else:
                            onym = onymOTH
                    else:
                        if onymB:
                            onym = onymOTH
                        else:
                            onym = None

                    from_csv = {
                        'word_forms_list': row[g('wordforms')],
                        'civil_equivalent': civilrus_convert(ENTRY.orthvars[0].idem),
                        'antconc_query': row[g('antconc')],
                        'editor': author,
                        'additional_info': additional_info,
                        'homonym_gloss': row[g('hom_gloss').strip()],
                        'homonym_order': hom_num,
                        'status': ccc,
                        'pos': pos,
                        'sg1': row[g('1sg')].strip(),
                        'sg2': row[g('2sg')].strip(),
                        'genitive': row[g('Gen')].strip(),
                        'nom_sg': row[g('NomSg')].strip(),
                        'gender': gender,
                        'tantum': tantum,
                        'short_form': row[g('short_form')],
                        'uninflected': get_bool(row[g('uninflected')]),
                        'onym': onym,
                    }
                    entry_args.update(from_csv)

                    entry = Entry.objects.create(**entry_args)
                    entry.save()

                    # Сохраняем орф.варианты
                    for ov in ENTRY.orthvars:
                        ov.entry=entry
                        ov.save()

                    # Этимология
                    etym = row[g('etym')].strip()
                    if etym:
                        greek = CategoryValue.objects.get(category_slug='language', slug='greek')
                        etym = Etymology(entry=entry, language=greek, text=etym,
                                         translit=u'', meaning=u'', gloss=u'', source=u'',
                                         unclear=False, questionable=False, mark=u'',
                                         additional_info=u'')
                        etym.save()

                    # Создаём значения. Пока даже если они пустые. Далее для пустых значений
                    # решение будет приниматься на основе наличия примеров.
                    L1 = ['m1', 'm2', 'm3', 'm4', 'm5']
                    L1 = [row[g(m)].strip() for m in L1]
                    L2 = ['gl1', 'gl2', 'gl3', 'gl4', 'gl5']
                    L2 = [row[g(gl)].strip() for gl in L2]

                    meaning_args = {
                        'metaphorical': False,
                        'substantivus': False,
                        'additional_info': u'',
                        'hidden': False,
                    }
                    meanings = [Meaning(entry=entry, meaning=i, gloss=j, **meaning_args) for i, j in zip(L1, L2)]

                    # Создаём примеры
                    # для значения 1
                    L1 = ['m1ex1', 'm1ex2', 'm1ex3', 'm1ex4', 'm1ex5', 'm1ex6', 'm1ex7', 'm1ex8']
                    L1 = [row[g(ex)].strip() for ex in L1]

                    L2 = ['m1adr1', 'm1adr2', 'm1adr3', 'm1adr4', 'm1adr5', 'm1adr6', 'm1adr7', 'm1adr8']
                    L2 = [row[g(adr)].strip() for adr in L2]

                    L3 = ['m1ctxt1', 'm1ctxt2', 'm1ctxt3', 'm1ctxt4', 'm1ctxt5', 'm1ctxt6', 'm1ctxt7', 'm1ctxt8']
                    L3 = [row[g(ctxt)].strip() for ctxt in L3]

                    L4 = ['m1gr1', 'm1gr2', 'm1gr3', 'm1gr4', 'm1gr5', 'm1gr6', 'm1gr7', 'm1gr8']
                    L4 = [row[g(gr)].strip() for gr in L4]

                    ex_args = {
                        'meaning': meanings[0],
                        'hidden': False,
                        'additional_info': u'',
                        'greek_eq_status': u'L',
                    }
                    examples = [Example(example=ex, context=ctxt,
                                        address_text=adr, **ex_args) for ex, adr, ctxt in zip(L1, L2, L3)]
                    ex_to_del = []
                    for n, ex in enumerate(examples_m1):
                        if not ex.example and not ex.context and not ex.address_text and not L4[n]:
                            ex_to_del.append(n)

                    for n, i in enumerate(ex_to_del):
                        x = i - n
                        del(L1[x], L2[x], L3[x], L4[x], examples[x])

                    if examples:
                        ex_args['meaning'].save()    
                        for n, ex in enumerate(examples):
                            ex.save()
                            if L4[n]:
                                gr = GreekEquivalentForExample(for_example=ex, text=L4[n], mark=u'',
                                                               source=u'', additional_info=u'')
                                gr.save()
                            
                    # для значения 2
                    L1 = ['m2ex1', 'm2ex2', 'm2ex3', 'm2ex4']
                    L1 = [row[g(ex)].strip() for ex in L1]

                    L2 = ['m2adr1', 'm2adr2', 'm2adr3', 'm2adr4']
                    L2 = [row[g(adr)].strip() for adr in L2]

                    L3 = ['m2ctxt1', 'm2ctxt2', 'm2ctxt3', 'm2ctxt4']
                    L3 = [row[g(ctxt)].strip() for ctxt in L3]

                    L4 = ['m2gr1', 'm2gr2', 'm2gr3', 'm2gr4']
                    L4 = [row[g(gr)].strip() for gr in L4]

                    ex_args['meaning'] = meanings[1],
                    examples = [Example(example=ex, context=ctxt,
                                        address_text=adr, **ex_args) for ex, adr, ctxt in zip(L1, L2, L3)]
                    ex_to_del = []
                    for n, ex in enumerate(examples):
                        if not ex.example and not ex.context and not ex.address_text and not L4[n]:
                            ex_to_del.append(n)

                    for n, i in enumerate(ex_to_del):
                        x = i - n
                        del(L1[x], L2[x], L3[x], L4[x], examples[x])

                    if examples:
                        ex_args['meaning'].save()    
                        for n, ex in enumerate(examples):
                            ex.save()
                            if L4[n]:
                                gr = GreekEquivalentForExample(for_example=ex, text=L4[n], mark=u'',
                                                               source=u'', additional_info=u'')
                                gr.save()

                    # для значений 3, 4, 5
                    for num in (3, 4, 5):
                        m = 'm' + str(num)
                        L1 = ['ex1', 'ex2', 'ex3']
                        L1 = [row[g(m + ex)].strip() for ex in L1]

                        L2 = ['adr1', 'adr2', 'adr3']
                        L2 = [row[g(m + adr)].strip() for adr in L2]

                        L3 = ['ctxt1', 'ctxt2', 'ctxt3']
                        L3 = [row[g(m + ctxt)].strip() for ctxt in L3]

                        L4 = ['gr1', 'gr2', 'gr3']
                        L4 = [row[g(m + gr)].strip() for gr in L4]

                        ex_args['meaning'] = meanings[num - 1],
                        examples = [Example(example=ex, context=ctxt,
                                            address_text=adr, **ex_args) for ex, adr, ctxt in zip(L1, L2, L3)]
                        ex_to_del = []
                        for n, ex in enumerate(examples):
                            if not ex.example and not ex.context and not ex.address_text and not L4[n]:
                                ex_to_del.append(n)

                        for n, i in enumerate(ex_to_del):
                            x = i - n
                            del(L1[x], L2[x], L3[x], L4[x], examples[x])

                        if examples:
                            ex_args['meaning'].save()
                            for n, ex in enumerate(examples):
                                ex.save()
                                if L4[n]:
                                    gr = GreekEquivalentForExample(for_example=ex, text=L4[n], mark=u'',
                                                                   source=u'', additional_info=u'')
                                    gr.save()

                    # Сохраняем все значения, которые непустые. Пустые значения,
                    # но с непустыми примерами должны были быть сохранены раньше.
                    for m in meanings:
                        if m.meaning or m.gloss:
                            m.save()

                    # Создаём метафорические значения.
                    L1 = ['mm1', 'mm2', 'mm3']
                    L1 = [row[g(m)].strip() for m in L1]

                    meaning_args = {
                        'metaphorical': True,
                        'substantivus': False,
                        'additional_info': u'',
                        'hidden': False,
                        'gloss': u'',
                    }
                    meanings = [Meaning(entry=entry, meaning=i, **meaning_args) for i in L1]

                    # Создаём примеры для метафорических значений
                    for num in (1, 2, 3):
                        m = 'mm' + str(num)
                        L1 = ['ex1', 'ex2', 'ex3']
                        L1 = [row[g(m + ex)].strip() for ex in L1]

                        L2 = ['adr1', 'adr2', 'adr3']
                        L2 = [row[g(m + adr)].strip() for adr in L2]

                        L3 = ['ctxt1', 'ctxt2', 'ctxt3']
                        L3 = [row[g(m + ctxt)].strip() for ctxt in L3]

                        L4 = ['gr1', 'gr2', 'gr3']
                        L4 = [row[g(m + gr)].strip() for gr in L4]

                        ex_args['meaning'] = meanings[num - 1],
                        examples = [Example(example=ex, context=ctxt,
                                            address_text=adr, **ex_args) for ex, adr, ctxt in zip(L1, L2, L3)]
                        ex_to_del = []
                        for n, ex in enumerate(examples):
                            if not ex.example and not ex.context and not ex.address_text and not L4[n]:
                                ex_to_del.append(n)

                        for n, i in enumerate(ex_to_del):
                            x = i - n
                            del(L1[x], L2[x], L3[x], L4[x], examples[x])

                        if examples:
                            ex_args['meaning'].save()
                            for n, ex in enumerate(examples):
                                ex.save()
                                if L4[n]:
                                    gr = GreekEquivalentForExample(for_example=ex, text=L4[n], mark=u'',
                                                                   source=u'', additional_info=u'')
                                    gr.save()

                    # Сохраняем все значения, которые непустые. Пустые значения,
                    # но с непустыми примерами должны были быть сохранены раньше.
                    for m in meanings:
                        if m.meaning or m.gloss:
                            m.save()

                    # Создаём словосочетания
                    cs = ['cg1', 'cg2', 'cg3']
                    cs = [row[g(x)].strip() for x in cs if row[g(x)].strip()]
                    cgs = [CollocationGroup(base_entry=entry) for x in cs]
                    cs = [Collocation(collogroup=cg, collocation=c,
                                      civil_equivalent=civilrus_convert(c)) for c, cg in (cs, cgs)]
                    for cg in cgs:
                        cg.save()

                    for c in cs:
                        c.save()


            if orthvar_collisions:
                response = HttpResponse(output.getvalue(), mimetype="text/csv")
                response['Content-Disposition'] = 'attachment; filename=%s--not.imported.csv' % datetime.datetime.strftime(datetime.datetime.now(), format='%Y.%m.%d--%H.%M.%S')
            else:
                response = HttpResponseRedirect('/')

            output.close()
            csvfile.close()
            return response
    else:
        form = BilletImportForm()
    return render_to_response('csv_import.html', {'form': form})
