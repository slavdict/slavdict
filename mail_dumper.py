# -*- coding: UTF-8 -*-
import os
import sys
import subprocess
import datetime
from django.core import mail, management
import settings
management.setup_environ(settings)

def check_output(*popenargs, **kwargs):
    r"""Run command with arguments and return its output as a byte string.

    Backported from Python 2.7 as it's implemented as pure python on stdlib.

    >>> output = check_output(['/usr/bin/python', '--version'])
    >>> output.startswith('Python 2.6')
    True
    """
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        error = subprocess.CalledProcessError(retcode, cmd)
        error.output = output
        raise error
    return output

if not hasattr(subprocess, 'check_output'):
    subprocess.check_output = check_output

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
