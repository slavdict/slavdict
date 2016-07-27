SHELL = /bin/bash

GITWORKTREE = /var/www/slavdict
GITDIR = /home/git/slavdict.www
SETTINGS_FILE = slavdict/settings.py
DATE_TIME := $(shell date +%Y-%m-%d--%H-%M)

SLAVDICT_ENVIRONMENT ?= production
IS_PRODUCTION = test ${SLAVDICT_ENVIRONMENT} = production || (echo "Окружение не является боевым" && exit 1)
IS_DEVELOPMENT = test ${SLAVDICT_ENVIRONMENT} = development || (echo "Окружение не являетя тестовым" && exit 1)

JSLIBS_PATH := $(shell python ${SETTINGS_FILE} --jslibs-path)
JSLIBS_VERSION_FILE := ${JSLIBS_PATH}version.txt
JSLIBS_NEW_VERSION := $(shell python ${SETTINGS_FILE} --jslibs-version)
JSLIBS_OLD_VERSION := $(shell cat ${JSLIBS_VERSION_FILE} 2>/dev/null)

LOCCHDIR = /root/slavdict-local-changes-untracked

restart: stop copydiff destroy_loc_changes checkout collectstatic fixown migrate start

run: collectstatic
	@echo "Запуск сервера в тестовом окружении..."
	@$(IS_DEVELOPMENT)
	compass watch &
	python ./manage.py runserver

stop:
	@$(IS_PRODUCTION)
	sudo service nginx stop
	sudo /etc/init.d/cherokee stop
	-sudo killall -9 uwsgi

start:
	sudo /etc/init.d/cherokee start
	curl slavdict.ruslang.ru:8088
	sudo service nginx start

copydiff:
	@$(IS_PRODUCTION)
	mkdir -p ${LOCCHDIR}
	git --work-tree=${GITWORKTREE} --git-dir=${GITDIR} \
		status -s | grep --color=never '?? ' | cut -c4- \
		| xargs -I '{}' rsync -av '{}' ${LOCCHDIR}/
	git --work-tree=${GITWORKTREE} --git-dir=${GITDIR} \
		diff --no-color >/root/slavdict-local-changes-${DATE_TIME}.diff

destroy_loc_changes:
	@$(IS_PRODUCTION)
	git --work-tree=${GITWORKTREE} --git-dir=${GITDIR} \
		reset --hard HEAD

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
	compass compile -e ${SLAVDICT_ENVIRONMENT}
	python ./manage.py collectstatic --noinput

migrate:
	python ./manage.py migrate

clean:
	-find -name '*.pyc' -execdir rm '{}' \;
	-rm -f static/*.css
	-rm -f ${JSLIBS_PATH}*.{js,map,txt}
	-rm -fR .sass-cache/
	-rm -fR .static/*

jslibs:
	if [ "${JSLIBS_OLD_VERSION}" != "${JSLIBS_NEW_VERSION}" ];\
	then \
		rm -f ${JSLIBS_PATH}*.{js,map,txt} ; \
		python ${SETTINGS_FILE} --jslibs | xargs -n3 wget ; \
		echo ${JSLIBS_NEW_VERSION} > ${JSLIBS_VERSION_FILE} ; \
	fi

scp:
	rsync bin/indesign_xml_dumper.py dilijnt0:/var/www/slavdict/bin/
	ssh dilijnt0 chown www-data:www-is /var/www/slavdict/bin/indesign_xml_dumper.py
	rsync -av templates/indesign dilijnt0:/var/www/slavdict/templates/
	ssh dilijnt0 chown -R www-data:www-is /var/www/slavdict/templates/indesign/

indesign:
	rsync -av bin dilijnt0:/var/www/slavdict/
	rsync -av slavdict/django_template_spaces dilijnt0:/var/www/slavdict/slavdict/
	rsync -av  templates/indesign dilijnt0:/var/www/slavdict/templates/
	rsync .list dilijnt0:/root/
	ssh dilijnt0 chown -R www-data:www-is /var/www/slavdict/
	ssh dilijnt0 nohup /var/www/slavdict/bin/remote_indesign_xml_dumper.sh
	scp dilijnt0:/root/slavdict-dump.xml ~/VirtualBox\ SharedFolder/slavdict-indesign.xml

listen-indesign:
	ls .list bin/indesign_xml_dumper.py templates/indesign/* | entr bash -c 'time cat .list | xargs python bin/indesign_xml_dumper.py >/home/nurono/VirtualBox\ SharedFolder/slavdict-indesign.xml'

.PHONY: \
    destroy_loc_changes \
    checkout \
    clean \
    collectstatic \
    copydiff \
    fixown \
    jslibs \
    listen-indesign \
    migrate \
    migrestart \
    restart \
    revert \
    _revert \
    run \
    start \
    stop \
    scp \


