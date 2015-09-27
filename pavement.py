import os
import sys
sys.path.append(os.getcwd())

from paver.easy import *
from slavdict.settings import *
import pry

@task
def prepare():
    import urllib

    """ Использование задачи jslibs

    Данный вывод в stdout используется в цели jslibs из Makefile.
    Вывод имеет следующий вид:

      [<ссылка на файл в интернете> -O <абс. имя файла в локальной ФС>]*

    Каждая такая тройка предназначена для wget. Он её будет получать
    следующим образом:

      python settings.py --jslibs | xargs -n3 wget

    От второго элемента тройки ("-O") отказаться не получилось, т.к.
    аргументы xargs -L или -n и -I не совместимы (см. man xargs /BUGS).
    Иначе можно было бы вместо троек использовать двойки и писать:

      python settings.py --jslibs | xargs -n2 -I{} wget {} -O {}

    """

    old_version = ''
    version_filename = "%s/version.txt" % JSLIBS_PATH
    try:
        with open(version_filename) as f:
            old_version = ''.join(f.readlines())
    except IOError:
        pass

    if JSLIBS_VERSION != old_version:
        clean()
        opener = urllib.URLopener()
        for lib in JSLIBS_LOCAL:
            url = JSLIBS_SOURCE[lib]
            filename = url.split('/')[-1]
            filepath = JSLIBS_PATH + filename

            if not os.path.isfile(filepath):
                opener.retrieve(url, filepath)
                print("Stored file %s" % filename)
        with open(version_filename, 'w') as f:
            f.write(JSLIBS_VERSION)

@task
def clean():
    import re
    rex = r"\.(js|map|txt|swf)$"
    dir = JSLIBS_PATH
    for f in os.listdir(dir):
        if re.search(rex, f):
            print f
            os.remove(os.path.join(dir, f))

@task
def environment():
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "slavdict.settings")
    django.setup()
