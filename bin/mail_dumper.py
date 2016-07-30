#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import datetime
import os
import subprocess
import sys
from os.path import basename, dirname, abspath, join

import django
from django.core import mail

sys.path.append(dirname(dirname(abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

from slavdict import settings

DUMP_SCRIPT = join(dirname(abspath(__file__)), 'dump.sh')
BACKUP_DIR = settings.BACKUP_DIR
GREP_SIGNATURE = ':::: '

output = subprocess.check_output([DUMP_SCRIPT, BACKUP_DIR], shell=True)
filepaths = [line[len(GREP_SIGNATURE):].strip()
             for line in output.splitlines()
             if line.startswith(GREP_SIGNATURE)]

if filepaths:
    connection = mail.get_connection()
    butime = datetime.datetime.now().strftime('%Y.%m.%d %H:%M')
    attachments = [(basename(path), open(path, 'rb').read(), None)
                   for path in filepaths]
    src_mail = 'autobackup@slavdict.ruslang.ru'
    dst_mails = [email for name, email in settings.BACKUP_MANAGERS]
    subject = '[slavdict backup] %s' % butime
    message = mail.EmailMessage(subject=subject, body='', from_email=src_mail,
                                to=dst_mails, attachments=attachments,
                                connection=connection)
    message.send()

sys.exit(0)
