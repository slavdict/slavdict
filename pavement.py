import os
import sys
sys.path.append(os.getcwd())

from paver.easy import *
from slavdict.settings import *
import pry

@task
#@needs(['environment'])
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
def jslibs_path():
    sys.stdout.write(JSLIBS_PATH)

@task
def jslibs_version():
    sys.stdout.write(JSLIBS_VERSION)

@task
def environment():
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "slavdict.settings")
    django.setup()

#from django_seed import Seed
#seeder = Seed.seeder()
#from django.contrib.auth.models import User
#from slavdict.custom_user.models import CustomUser
#from django.contrib.auth.hashers import make_password
#seeder.add_entity(User, 1)
#seeder.add_entity(CustomUser, 1, {
#    'password':    lambda x: make_password('12345678'),
#    'second_name':    lambda x: seeder.faker.name(),
#})
#inserted_pks = seeder.execute()

#import sqlite3
#conn = sqlite3.connect('.test.db')
#c = conn.cursor()
#c.execute("INSERT INTO auth_user VALUES ('12345678','',True,'majioa','Malo','Skrylevo','majioa@yandex.ru',True,True,'')")
#c.execute("INSERT INTO stocks VALUES ('2006-01-05','BUY','RHAT',100,35.14)")
#conn.commit()
#conn.close()

#pry()

@task
def clean():
    import re
    rex = r"\.(js|map|txt|swf)$"
    dir = JSLIBS_PATH
    for f in os.listdir(dir):
        if re.search(rex, f):
            print f
            os.remove(os.path.join(dir, f))
