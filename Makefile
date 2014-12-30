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

restart: stop checkout collectstatic fixown migrate start

run: collectstatic
	@echo "Запуск сервера в тестовом окружении..."
	@$(IS_DEVELOPMENT)
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
	chmod u+x ./*.sh

collectstatic: jslibs
	compass compile -e ${SLAVDICT_ENVIRONMENT}
	python ./manage.py collectstatic --noinput

migrate:
	python ./manage.py migrate

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


