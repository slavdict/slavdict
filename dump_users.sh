#!/bin/bash
NOW=$(date +"%Y.%m.%d--%H.%M")
PRJDIR="$( cd "$( dirname "$0" )" && pwd )" # ... dirname "$( readlink -f "$0" )" ...
DUMPDIR="$PRJDIR/.dumps"
LASTFILE=$(ls -tA $DUMPDIR/.users*.xml | head -1)
FILE="$DUMPDIR/.users--$NOW.xml"

python $PRJDIR/manage.py dumpdata auth.User auth.Group custom_user.CustomUser --format=xml --indent=4 > $FILE

if [ "$LASTFILE" -a "$FILE" != "$LASTFILE" ]
then
    x=$(diff $FILE $LASTFILE)

    if [ -z "$x" ]; then
        rm $FILE
    else
        echo "::$FILE"
    fi
fi
