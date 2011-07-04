# -*- coding: utf-8 -*-

from dictionary.forms import BilletImportForm
from django.http import HttpResponse, HttpResponseRedirect
import slavdict.unicode_csv as unicode_csv
import StringIO

from custom_user.models import CustomUser
from slavdict.directory.models import CategoryValue
ccc = CategoryValue.objects.get(pk=46) # Импортирована (Статус статьи "Статья импортирована из Moodle")

from slavdict.dictionary.models import entry_dict

@login_required
def import_moodle_base(request):

    if request.method == 'POST':
        form = BilletImportForm(request.POST, request.FILES)
        if form.is_valid():

            csvfile = request.FILES['csvfile']
            csv_reader = unicode_csv.UnicodeReader(csvfile, dialect=unicode_csv.calc, encoding='utf-8')

            output = StringIO.StringIO()
            csv_writer = unicode_csv.UnicodeWriter(output, dialect=unicode_csv.calc, encoding='utf-8')

            csv_writer.writerow(csv_reader.next()) # Первую строку, в ней обязаны быть заголовки,
            # упреждающе записываем в возможный файл возврата конфликтующих csv-записей.

            idems = OrthographicVariant.objects.all().values_list('idem') # Список списков, каждый из которых содержит один элемент.
            idems = [x[0] for x in idems] # Переходим от списка списков к списку самих элементов (орфографических вариантов).
            authors = CustomUser.objects.all()

            collision_orthvars = []
            csv_authors = {}

            for row in csv_reader:
                # Столбцы в CSV-файле
                orthvar, civil_equivalent, word_forms_list, antconc_query, author_in_csv, additional_info = row

                if orthvar in idems:
                    collision_orthvars.append(idems.index(orthvar))
                    csv_writer.writerow(row)
                else:
                    if author_in_csv in csv_authors:
                        author = csv_authors[author_in_csv]
                    else:
                        for au in authors:
                            if au.last_name and author_in_csv.startswith(au.last_name):
                                author = au
                                csv_authors[author_in_csv] = au
                                break
                        else:
                            raise NameError(u"Автор, указанный в CSV-файле, не найден среди участников работы над словарём.")

                    entry_args = entry_dict.copy() # Поверхностная (!) копия словаря.
                    entry_args['status'] = ccc
                    # Все булевские переменные уже выставлены по умолчанию в False в entry_dict

                    from_csv = {
                        'word_forms_list': word_forms_list,
                        'civil_equivalent': civil_equivalent,
                        'antconc_query': antconc_query,
                        'editor': author,
                        'additional_info': additional_info,
                    }
                    entry_args.update(from_csv)

                    entry = Entry.objects.create(**entry_args)
                    entry.save()

                    ov = OrthographicVariant.objects.create(entry=entry, idem=orthvar)
                    ov.save()

            if collision_orthvars:
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
