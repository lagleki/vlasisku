#!/bin/bash

exec 2>&1
set -e
set -x

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

./fix_selinux.sh

echo
echo "Launching docker bots inside the previous docker instance"
echo

sudo docker exec -i $hasterm lojban_vlasisku${test} bash -c "cd /srv/lojban/vlasisku ; ./manage.py runbots"
