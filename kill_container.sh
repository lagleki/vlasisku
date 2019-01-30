#!/bin/bash

exec 2>&1
set -x

CONTAINER_BIN=${CONTAINER_BIN:-$(which podman)}
CONTAINER_BIN=${CONTAINER_BIN:-$(which docker)}

test=""
# Test mode
if [ "$1" = "-t" ]
then
	test="_test"
fi

sudo $CONTAINER_BIN stop --time=30 lojban_vlasisku${test}
sudo $CONTAINER_BIN kill lojban_vlasisku${test}
sudo $CONTAINER_BIN rm lojban_vlasisku${test}

exit 0
