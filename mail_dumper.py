# -*- coding: UTF-8 -*-
import os
import sys
import subprocess
import datetime
from django.core import mail, management
from slavdict import settings
management.setup_environ(settings)

output = subprocess.check_output('./dump.sh', shell=True)
filepaths = [L[2:].strip() for L in output.splitlines() if L.startswith('::')]

if filepaths:
    connection = mail.get_connection()
    butime = datetime.datetime.now().strftime('%Y.%m.%d %H:%M')
    attachments = [(os.path.basename(path), open(path, 'rb').read(), None) for path in filepaths]
    emails = [email for name, email in settings.BACKUP_MANAGERS]
    message = mail.EmailMessage(
        '[slavdict backup] %s' % butime,
        '',
        'autobackup@slavonic.makd.ru',
        emails,
        attachments=attachments,
        connection=connection,
    )
    message.send()

sys.exit(0)
