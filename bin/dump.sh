#!/bin/bash
PRJDIR=$(dirname "$(readlink -m "$0")")
$PRJDIR/dump_users.sh
$PRJDIR/dump_dictionary.sh
