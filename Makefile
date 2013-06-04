SHELL = /bin/bash

GITWORKTREE = /var/www/slavdict
GITDIR = /home/git/slavdict.www
SLAVDICT_ENVIRONMENT ?= production
IS_PRODUCTION = test ${SLAVDICT_ENVIRONMENT} = production || (echo "Окружение не является боевым" && exit 1)
IS_DEVELOPMENT = test ${SLAVDICT_ENVIRONMENT} = development || (echo "Окружение не являетя тестовым" && exit 1)

run:
	@echo "Запуск сервера в тестовом окружении..."
	@$(IS_DEVELOPMENT)
	compass compile -e development
	python ./manage.py collectstatic --noinput
	python ./manage.py runserver

stop:
	@$(IS_PRODUCTION)
	sudo /etc/init.d/cherokee stop
	-sudo killall -9 uwsgi

start:
	sudo /etc/init.d/cherokee start

checkout:
	@$(IS_PRODUCTION)
	git --work-tree=${GITWORKTREE} --git-dir=${GITDIR} \
		pull origin master
	compass compile -e production
	python ./manage.py collectstatic --noinput
	chown -R www-data:www-is ./
	chown -R git:www-is /home/git/slavdict.*
	chmod u+x ./*.sh

revert:
	@$(IS_PRODUCTION)
	git --work-tree=${GITWORKTREE} --git-dir=${GITDIR} \
		reset --hard HEAD^
	compass compile -e production
	python ./manage.py collectstatic --noinput
	chown -R www-data:www-is ./
	chown -R git:www-is /home/git/slavdict.*
	chmod u+x ./*.sh

syncdb:
	python ./manage.py syncdb

migrate:
	python ./manage.py migrate dictionary

restart: stop checkout syncdb start

migrestart: stop checkout syncdb migrate start

clean:
	-find -name '*.pyc' -execdir rm {} \;
	-rm -f static/*.css
	-rm -fR .sass-cache/
	-rm -fR .static/*

.PHONY: \
    checkout \
    clean \
    migrate \
    migrestart \
    restart \
    run \
    start \
    stop \
    syncdb \


