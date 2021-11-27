#!/bin/bash
PRJDIR=$(dirname "$(dirname "$(readlink -e "$0")")")
DUMPDIR="${1:-$PRJDIR/.dumps}"
DICTDIR=$DUMPDIR/slavdict_generated
CSLDIR=$DUMPDIR/refs

EXEC=python
python -m django >/dev/null 2>&1 || EXEC='pipenv run python'

if test "$1" != "refs"
then
    $EXEC $PRJDIR/bin/csl_dict_dumper.py --output-dir=$DICTDIR
endif
$EXEC $PRJDIR/bin/csl_refs_dumper.py --output-dir=$CSLDIR
