SHELL = /bin/bash

GITWORKTREE = /var/www/slavdict
GITDIR = /home/git/slavdict.www

SLAVDICT_ENVIRONMENT ?= production
IS_PRODUCTION = test ${SLAVDICT_ENVIRONMENT} = production || (echo "Окружение не является боевым" && exit 1)
IS_DEVELOPMENT = test ${SLAVDICT_ENVIRONMENT} = development || (echo "Окружение не являетя тестовым" && exit 1)

JSLIBS_PATH := $(shell python settings.py --jslibs-path)
JSLIBS_VERSION_FILE := ${JSLIBS_PATH}version.txt
JSLIBS_NEW_VERSION := $(shell python settings.py --jslibs-version)
JSLIBS_OLD_VERSION := $(shell cat ${JSLIBS_VERSION_FILE} 2>/dev/null)

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
	-rm -f ${JSLIBS_PATH}*.{js,map,txt}
	-rm -fR .sass-cache/
	-rm -fR .static/*

jslibs:
	test "${JSLIBS_OLD_VERSION}" == "${JSLIBS_NEW_VERSION}" \
	|| ( \
		rm -f ${JSLIBS_PATH}*.{js,map,txt} ; \
		python settings.py --jslibs | xargs -n3 wget ; \
		echo ${JSLIBS_NEW_VERSION} > ${JSLIBS_VERSION_FILE} \
	)

.PHONY: \
    checkout \
    clean \
    jslibs \
    migrate \
    migrestart \
    restart \
    run \
    start \
    stop \
    syncdb \


