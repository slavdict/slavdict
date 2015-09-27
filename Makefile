SHELL = /bin/bash

GITWORKTREE = /var/www/slavdict
GITDIR = /home/git/slavdict.www

SLAVDICT_ENVIRONMENT ?= production
IS_PRODUCTION = test ${SLAVDICT_ENVIRONMENT} = production || (echo "Окружение не является боевым" && exit 1)
IS_DEVELOPMENT = test ${SLAVDICT_ENVIRONMENT} = development || (echo "Окружение не являетя тестовым" && exit 1)

restart: stop checkout collectstatic fixown migrate start

run: collectstatic
	@echo "Запуск сервера в тестовом окружении..."
	@$(IS_DEVELOPMENT)
	compass watch &
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

_revert:
	@$(IS_PRODUCTION)
	git --work-tree=${GITWORKTREE} --git-dir=${GITDIR} \
		reset --hard HEAD^

revert: _revert collectstatic fixown

fixown:
	@$(IS_PRODUCTION)
	chown -R www-data:www-is ./
	chown -R git:www-is /home/git/slavdict.*
	chmod u+x bin/*.sh

collectstatic: jslibs
	./manage.py compass
	./manage.py collectstatic --noinput

migrate:
	./manage.py migrate

clean:
	-find -name '*.pyc' -execdir rm '{}' \;
	-rm -f static/*.css
	-rm -fR .sass-cache/
	-rm -fR .static/*
	paver clean

jslibs:
	SLAVDICT_ENVIRONMENT=production paver prepare

.PHONY: \
    checkout \
    clean \
    collectstatic \
    fixown \
    jslibs \
    migrate \
    migrestart \
    restart \
    revert \
    _revert \
    run \
    start \
    stop \


