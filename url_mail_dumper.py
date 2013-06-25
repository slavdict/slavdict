# -*- coding: UTF-8 -*-
import cStringIO
import datetime
import gzip
import os
import sys

from django.core import mail
from django.core.management import call_command
from django.core.management import setup_environ

from slavdict import settings

setup_environ(settings)

users = cStringIO.StringIO()
dictionary = cStringIO.StringIO()
users_gz = gzip.GzipFile(fileobj=users, mode='wb')
dictionary_gz = gzip.GzipFile(fileobj=dictionary, mode='wb')

sys.stdout = users_gz
call_command('dumpdata', 'custom_user', format='xml', indent=2)
sys.stdout = sys.__stdout__
users_gz.close()
users.seek(0)

sys.stdout = dictionary_gz
call_command('dumpdata', 'dictionary', format='xml', indent=2)
sys.stdout = sys.__stdout__
dictionary_gz.close()
dictionary.seek(0)

connection = mail.get_connection()
butime = datetime.datetime.now().strftime('%Y.%m.%d %H:%M')
attachments = (
    ('dictionary %s.xml.gz', users.read(), 'application/gzip'),
    ('users %s.xml.gz', dictionary.read(), 'application/gzip'),
)
emails = [email for name, email in settings.BACKUP_MANAGERS]
message = mail.EmailMessage(
    '[slavdict backup] %s' % butime,
    '',
    'autobackup@slavdict.ruslang.ru',
    emails,
    attachments=attachments,
    connection=connection,
)
message.send(fail_silently=True)

os._exit(0)
