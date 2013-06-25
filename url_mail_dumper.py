# -*- coding: UTF-8 -*-
import cStringIO
import datetime
import os
import sys

from django.core import mail
from django.core.management import call_command
from django.core.management import setup_environ

from slavdict import settings

setup_environ(settings)
users_data = cStringIO.StringIO()
dictionary_data = cStringIO.StringIO()

sys.stdout = users_data
call_command('dumpdata', 'custom_user', format='xml', indent=2)
users_data.seek(0)
sys.stdout = dictionary_data
call_command('dumpdata', 'dictionary', format='xml', indent=2)
dictionary_data.seek(0)
sys.stdout = sys.__stdout__

connection = mail.get_connection()
butime = datetime.datetime.now().strftime('%Y.%m.%d %H:%M')
attachments = (
    ('dictionary %s.xml', users_data.read(), 'application/xml'),
    ('users %s.xml', dictionary_data.read(), 'application/xml'),
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
