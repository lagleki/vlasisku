#!/bin/bash

exec 2>&1
set -e
set -x

./kill_docker.sh "$@"

./build_docker.sh "$@"

test=""
# Test mode
if [ "$1" = "-t" ]
then
	test="_test"
fi

# if [ "$test" ]
# then
# 	echo "Copying web data to test folders."
# 	rsync -aHAX --delete /srv/lojban/mediawiki-docker/data/files/ /srv/lojban/mediawiki-docker/data/files$test/
# 	rsync -aHAX --delete /srv/lojban/mediawiki-docker/data/images/ /srv/lojban/mediawiki-docker/data/images$test/
# fi

web_port=12080
if [ "$test" ]
then
	web_port=12081
fi

# our sub-version number; used to force rebuilds
# MUST change this both here and in build_web.sh
ITERATION=1

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
echo "Launching website docker, which will listen on web_port $web_port"
echo

sudo docker run --name lojban_vlasisku${test} -p $web_port:8080 \
	-v /srv/lojban/vlasisku:/srv/lojban/vlasisku \
	-i $hasterm lojban/vlasisku:$ITERATION \
	bash -c "/srv/lojban/vlasisku/manage.py runserver -h 0.0.0.0 -p 8080 --threaded --passthrough-errors -D -r"
