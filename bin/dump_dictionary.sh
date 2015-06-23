#!/bin/bash
DBS_VERSION=4.05
GREP_SIGNATURE=::::
NOW=$(date +"%Y.%m.%d--%H.%M")
PRJDIR=$(dirname "$(dirname "$(readlink -e "$0")")")
DUMPDIR="${1:-$PRJDIR/.dumps}"
LASTFILE=$(ls -tA $DUMPDIR/.dictionary*.xml | head -1)
FILE="$DUMPDIR/.dictionary--$NOW---$DBS_VERSION.xml"

python $PRJDIR/manage.py dumpdata dictionary --format=xml --indent=4 > $FILE

if [ "$LASTFILE" ]
then
    if [ "$FILE" != "$LASTFILE" ]
    then
        x=$(diff $FILE $LASTFILE)

        if [ -z "$x" ]
        then
            rm $FILE
        else
            gzip -c $FILE > $FILE.gz
            echo "$GREP_SIGNATURE $FILE.gz"

            if [ -a $LASTFILE.gz ]
            then
                rm $LASTFILE
            fi
        fi
    fi
else
    gzip -c $FILE > $FILE.gz
    echo "$GREP_SIGNATURE $FILE.gz"
fi
