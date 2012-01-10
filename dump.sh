#!/bin/bash
PRJDIR="$( cd "$( dirname "$0" )" && pwd )" # ... dirname "$( readlink -f "$0" )" ...
$PRJDIR/dump_users.sh
$PRJDIR/dump_directory.sh
$PRJDIR/dump_dictionary.sh
