#!/bin/bash
NOW=$(date +"%Y.%m.%d--%H.%M")
PRJDIR=$(dirname "$(readlink -m "$0")")
DUMPDIR="$PRJDIR/.dumps"
LASTFILE=$(ls -tA $DUMPDIR/.users*.xml | head -1)
FILE="$DUMPDIR/.users--$NOW.xml"

python $PRJDIR/manage.py dumpdata auth.User auth.Group custom_user.CustomUser --format=xml --indent=4 > $FILE

if [ "$LASTFILE" -a "$FILE" != "$LASTFILE" ]
then
    x=$(diff -I ".*last_login.*" $FILE $LASTFILE)

    if [ -z "$x" ]; then
        rm $FILE
    else
        echo "::$FILE"
    fi
fi
