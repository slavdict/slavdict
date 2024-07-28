#!/bin/bash
PRJDIR=$(dirname "$(dirname "$(readlink -e "$0")")")
MIGRATION_VERSION=$(basename "$(ls "$PRJDIR"/slavdict/dictionary/migrations/????_*.py | tail -1)" | cut -d_ -f1)
DBS_VERSION=4.$MIGRATION_VERSION
GREP_SIGNATURE=::::
NOW=$(date +"%Y.%m.%d--%H.%M")
DUMPDIR="${1:-$PRJDIR/.dumps}"
VERBOSITY=${2:-0}
MODELS=(
    collocation
    collocationgroup
    entry
    etymology
    example
    greekequivalentforexample
    meaning
    meaningcontext
    orthographicvariant
    participle
    tempedit
    tip
    translation
    translationsource
)

EXEC=python
python -m django >/dev/null 2>&1 || EXEC='pipenv run python'

for model in ${MODELS[*]}
do
    FILE="$DUMPDIR/dictionary--$NOW---$DBS_VERSION--$model.xml"
    echo $FILE
    $EXEC $PRJDIR/manage.py dumpdata --verbosity=$VERBOSITY \
        dictionary.$model --natural-foreign --format=xml --indent=2 > $FILE
done

FILE="$DUMPDIR/dictionary--$NOW---$DBS_VERSION.tar.gz"
tar -czvf $FILE $DUMPDIR/dictionary--$NOW---$DBS_VERSION--*.xml
echo "$GREP_SIGNATURE $FILE"
