#!/bin/bash
PRJDIR=$(dirname "$(dirname "$(readlink -e "$0")")")
DUMPDIR="${1:-$PRJDIR/.dumps}"
$PRJDIR/bin/dump_users.sh $DUMPDIR
$PRJDIR/bin/dump_dictionary.sh $DUMPDIR
