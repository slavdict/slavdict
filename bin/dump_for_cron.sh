service nginx stop
service uwsgi stop slavdict
/usr/bin/python /var/www/slavdict/bin/mail_dumper.py
service uwsgi start slavdict
service nginx start
