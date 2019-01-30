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

# our container build version number; used to force rebuilds
ITERATION=1

echo
echo "Building vlasisku container."
echo

sudo $CONTAINER_BIN build --build-arg=VS_USERID=$(id -u) --build-arg=VS_GROUPID=$(id -g) \
	-t lojban/vlasisku:$ITERATION \
	-f Dockerfile .
