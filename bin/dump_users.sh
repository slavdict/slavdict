#!/bin/bash
GREP_SIGNATURE=::::
NOW=$(date +"%Y.%m.%d--%H.%M")
PRJDIR=$(dirname "$(dirname "$(readlink -e "$0")")")
DUMPDIR="${1:-$PRJDIR/.dumps}"
LASTFILE=$(ls -tA $DUMPDIR/.users*.xml | head -1)
FILE="$DUMPDIR/.users--$NOW.xml"

EXEC=python
python -m django >/dev/null 2>&1 || EXEC='pipenv run python'

$EXEC $PRJDIR/manage.py dumpdata \
    auth.User auth.Group custom_user.CustomUser \
    --format=xml --indent=4 > $FILE

if [ "$LASTFILE" ]
then
    if [ "$FILE" != "$LASTFILE" ]
    then
        x=$(diff -I ".*last_login.*" $FILE $LASTFILE)

        if [ -z "$x" ]
        then
            rm $FILE
        else
            echo "$GREP_SIGNATURE $FILE"
        fi
    fi
else
    echo "$GREP_SIGNATURE $FILE"
fi
