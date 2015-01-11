#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
import datetime
import os
import subprocess
import sys
from os.path import basename, dirname, abspath, join

import django
from django.core import mail

from slavdict import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'slavdict.settings')
django.setup()

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

DUMP_SCRIPT = join(dirname(abspath(__file__)), 'dump.sh')
BACKUP_DIR = settings.BACKUP_DIR
GREP_SIGNATURE = ':::: '
output = subprocess.check_output([DUMP_SCRIPT, BACKUP_DIR], shell=True)
filepaths = [line[len(GREP_SIGNATURE):].strip() for line in output.splitlines()
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
