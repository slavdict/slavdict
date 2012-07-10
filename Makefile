GITWORKTREE=/var/www/slavdict
GITDIR=/home/git/slavdict.www

rundj:
	@echo Running Django:
	sass --update static
	python ./manage.py collectstatic --noinput
	python ./manage.py runserver

stop:
	sudo /etc/init.d/cherokee stop
	sudo killall -9 uwsgi

start:
	sudo /etc/init.d/cherokee start

checkout:
	git --work-tree=${GITWORKTREE} --git-dir=${GITDIR} \
		pull origin master
	sass update --static
	python ./manage.py collectstatic --noinput
	chown -R www-data:www-is ./
	chown -R git:www-is /home/git/slavdict.*
	chmod u+x ./*.sh

syncdb:
	python ./manage.py syncdb

migrate:
	python ./manage.py migrate dictionary

restart: stop checkout syncdb start

migrastart: stop checkout syncdb migrate start

.PHONY: rundj stop checkout syncdb migrate start restart migrastart
