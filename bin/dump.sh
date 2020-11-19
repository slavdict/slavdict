#!/bin/bash
PRJDIR=$(dirname "$(dirname "$(readlink -e "$0")")")
DUMPDIR="${1:-$PRJDIR/.dumps}"
VERBOSITY=${2:-0}
$PRJDIR/bin/dump_csl.sh $DUMPDIR $VERBOSITY
$PRJDIR/bin/dump_users.sh $DUMPDIR
$PRJDIR/bin/dump_dictionary.sh $DUMPDIR $VERBOSITY
find $DUMPDIR \
  -mindepth 1 \
  -and -mtime -93 \
  -and ! -name .rsync-filter \
  -and ! -name 'dictionary*.xml' \
  | xargs basename -a
  | sed -e 's/^/+ /; $s/$/\n- */' \
  > $DUMPDIR/.rsync-filter
