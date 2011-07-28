#!/bin/bash
NOW=$(date +"%Y.%m.%d--%H.%M")
DBS_VERSION=14
PRJDIR="/var/www/slavdict"
DUMPDIR="$PRJDIR/.dumps"
FILE=".dictionary--$NOW---$DBS_VERSION.xml"
python $PRJDIR/manage.py dumpdata dictionary --format=xml --indent=4 > $DUMPDIR/$FILE
