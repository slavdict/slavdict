#!/bin/bash
PRJDIR=$(dirname "$(dirname "$(readlink -e "$0")")")
MIGRATION_VERSION=$(basename "$(ls "$PRJDIR"/slavdict/csl_annotations/migrations/????_*.py | tail -1)" | cut -d_ -f1)
DBS_VERSION=1.$MIGRATION_VERSION
GREP_SIGNATURE=::::
NOW=$(date +"%Y.%m.%d--%H.%M")
DUMPDIR="${1:-$PRJDIR/.dumps}"
LASTFILE=$(ls -tA "$DUMPDIR"/csl*.xml | head -1)
FILE="$DUMPDIR/csl--$NOW---$DBS_VERSION.xml"
VERBOSITY=${2:-0}

EXEC=python
python -m django >/dev/null 2>&1 || EXEC='pipenv run python'

$EXEC $PRJDIR/manage.py dumpdata --verbosity=$VERBOSITY \
    csl_annotations --all --natural-foreign --format=xml --indent=4 > $FILE

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
