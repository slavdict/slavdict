## SlavDict

Добро пожаловать в проект славянского словаря.

### Устаноква

Отзеркальте себе проект так:

    $ git clone git@github.com:while0pass/slavdict.git
    Cloning into 'slavdict'...
    done.

Войдите в папку проекта:

    $ cd slavdict

Сойздайте окружение питоновских пакетов для проекта в virtualenv:

    $ virtualenv --no-site-packages --prompt="[slavdict]" .venv
    New python executable in .venv/bin/python2.7
    Also creating executable in .venv/bin/python
    Installing setuptools, pip...done.

Задействуйте его:

    $ . .venv/bin/activate

Установите в окружение зависимые от приложения пакеты (яйца) питоньи:

    $ pip install -r requirements.txt
    # Некоторый лог установки пакетов
    Installing collected packages: MarkupSafe, Coffin, pry, paver, django-compass2, HIP2Unicode, Jinja2, psycopg2, Django
    Running setup.py install for MarkupSafe
      building 'markupsafe._speedups' extension
      # ...
    Running setup.py install for Coffin
    Running setup.py install for pry
    Running setup.py install for django-compass2
    Running setup.py install for HIP2Unicode
    Running setup.py install for psycopg2
      building 'psycopg2._psycopg' extension
      # ...
    Successfully installed Coffin-0.3.8 Django-1.7.9 HIP2Unicode-1.0.0 Jinja2-2.8 MarkupSafe-0.23 django-compass2-0.2 paver-1.2.4 pry-0.0.1 psycopg2-2.6.1

ну или так:

    $ while read line; do easy_install "$line"; done < requirements.txt

Обязательно экспортируйте секретный ключ в переменную окружения SLAVDICT_SECRET_KEY так:

    $ export SLAVDICT_SECRET_KEY='<your_secret_key>'

где `<your_secret_key>` требуемое значение.

Установка завершена, далее следуйте пунктам настройки.

### Настройка

По умолчанию есть 3 рабочих окружения проекта: боевое (production), отладочное (development), тестовое (test).
Окружением по умолчанию является отладочным.

Первым шагом настойки является создание базы данных проекта. Делается оное, из корневой папки, так:

    $ ./manage.py migrate

    Operations to perform:
    Synchronize unmigrated apps: djcompass
    Apply all migrations: dictionary, sessions, admin, auth, contenttypes, custom_user
    Synchronizing apps without migrations:
    Creating tables...
    Installing custom SQL...
    Installing indexes...
    Running migrations:
    Applying contenttypes.0001_initial... OK
    Applying auth.0001_initial... OK
    Applying admin.0001_initial... OK
    Applying custom_user.0001_initial... OK
    Applying dictionary.0001_initial... OK
    Applying dictionary.0002_extend_substantivus_types... OK
    Applying dictionary.0003_auto_20150601_2300... OK
    Applying dictionary.0004_auto_20150616_0706... OK
    Applying dictionary.0005_auto_20150616_0711... OK
    Applying sessions.0001_initial... OK

Сим шагом будет создан файл базы данных (sqlite3) `.development.db`, название коего определяется наимменованием окружения.
Чтобы удалить базу, достаточно просто удалить файл базы данных соотвествующий окружению. После чего можно её пересоздать заново.

Соберите набор каскадных стилей из исходников:

    $ ./manage.py compass
    directory static/css
    write static/css/fix_admin.css
    write static/css/flex.css
    write static/css/hellinist_workbench.css
    write static/css/style.css

Для завершения настройки боевого окружения требудется выполнить ещё несколько шагов.
Таковой как: подготовка постоянных файлов небходимых для запуск в боевом режиме. Делается оная так:

    $ SLAVDICT_ENVIRONMENT=production paver prepare
    ---> pavement.prepare
    ---> pavement.clean
    Stored file knockout.mapping-latest.js
    Stored file knockout-sortable.min.js
    Stored file knockout-postbox.min.js
    Stored file ZeroClipboard.min.js
    Stored file ZeroClipboard.swf
    Stored file opentip-jquery.min.js
    Stored file opentip-jquery-excanvas.min.js

Вы также можете очистить дерево проекта от постоянных файлов, сохранённых по причине выполнения предыдущей команды, так:

    $ paver clean
    ---> pavement.clean
    opentip-jquery-excanvas.min.js
    ZeroClipboard.min.js
    ZeroClipboard.swf
    knockout-postbox.min.js
    knockout.mapping-latest.js
    knockout-sortable.min.js
    opentip-jquery.min.js
    version.txt

### Запуск

Запустить в работу в отладочном окружении проект можно так:

    $ make run
    # некоторый вывод

или без мониторинга стилей так:

    $ ./manage.py runserver
    System check identified 2 issues (0 silenced).
    August 12, 2015 - 20:28:27
    Django version 1.7.9, using settings 'slavdict.settings'
    Starting development server at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Запуск в боевом окружении делается так:

    $ make start

или если нужен перезапуск, то так:

    $ make restart
