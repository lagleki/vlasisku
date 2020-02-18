#!/bin/bash

exec 2>&1
set -e
set -x

CONTAINER_BIN=${CONTAINER_BIN:-$(which podman)}
CONTAINER_BIN=${CONTAINER_BIN:-$(which docker)}

test=""
# Test mode
if [ "$1" = "-t" ]
then
	test="_test"
fi

# Ask for a tty if that makes sense
hasterm=''
if tty -s
then
	hasterm='-t'
fi

echo
echo "Setting up config files and the like."
echo

cd /srv/lojban/vlasisku
./fix_selinux.sh

echo
echo "Killing container bots inside the previous container instance"
echo

while $CONTAINER_BIN exec -i $hasterm lojban_vlasisku${test} pgrep -f runbots
do
	$CONTAINER_BIN exec -i $hasterm lojban_vlasisku${test} pkill -f runbots || true
	sleep 1
	$CONTAINER_BIN exec -i $hasterm lojban_vlasisku${test} pkill -9 -f runbots || true
done

$CONTAINER_BIN exec -i $hasterm lojban_vlasisku${test} pgrep -f runbots || exit 0
