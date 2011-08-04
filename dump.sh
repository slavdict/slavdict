#!/bin/bash
NOW=$(date +"%Y.%m.%d--%H.%M")
DBS_VERSION=16
PRJDIR="$( cd "$( dirname "$0" )" && pwd )" # ... dirname "$( readlink -f "$0" )" ...
DUMPDIR="$PRJDIR/.dumps"
LASTFILE=$(ls -tA $DUMPDIR/.dictionary*.xml | head -1)
FILE=".dictionary--$NOW---$DBS_VERSION.xml"

python $PRJDIR/manage.py dumpdata dictionary --format=xml --indent=4 > $DUMPDIR/$FILE

if [ "$LASTFILE" -a "$FILE" != "$LASTFILE" ]
then
    x=$(diff $DUMPDIR/$FILE $DUMPDIR/$LASTFILE)

    if [ -z "$x" ]
    then rm $DUMPDIR/$FILE
    else
        if [ -a $DUMPDIR/$LASTFILE.gz ]
        then rm $DUMPDIR/$LASTFILE
        fi
    fi
fi

gzip -c $DUMPDIR/$FILE > $DUMPDIR/$FILE.gz
