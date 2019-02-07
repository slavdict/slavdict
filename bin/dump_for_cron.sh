/usr/sbin/service nginx stop
/usr/sbin/service uwsgi stop slavdict
/usr/bin/python /var/www/slavdict/bin/mail_dumper.py
/usr/sbin/service uwsgi start slavdict
/usr/sbin/service nginx start
