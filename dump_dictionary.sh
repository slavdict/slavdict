#!/bin/bash
NOW=$(date +"%Y.%m.%d--%H.%M")
DBS_VERSION=16
PRJDIR="$( cd "$( dirname "$0" )" && pwd )" # ... dirname "$( readlink -f "$0" )" ...
DUMPDIR="$PRJDIR/.dumps"
LASTFILE=$(ls -tA $DUMPDIR/.dictionary*.xml | head -1)
FILE="$DUMPDIR/.dictionary--$NOW---$DBS_VERSION.xml"

python $PRJDIR/manage.py dumpdata dictionary --format=xml --indent=4 > $FILE

if [ "$LASTFILE" -a "$FILE" != "$LASTFILE" ]
then
    x=$(diff $FILE $LASTFILE)

    if [ -z "$x" ]
    then rm $FILE
    else
        gzip -c $FILE > $FILE.gz
    
        if [ -a $LASTFILE.gz ]
        then rm $LASTFILE
        fi
    fi
fi
