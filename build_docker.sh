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

# our docker build version number; used to force rebuilds
ITERATION=1

echo
echo "Building vlasisku docker."
echo

sudo docker build --build-arg=VS_USERID=$(id -u) --build-arg=VS_GROUPID=$(id -g) \
	-t lojban/vlasisku:$ITERATION \
	-f Dockerfile .
