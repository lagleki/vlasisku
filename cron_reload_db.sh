#!/bin/sh

CONTAINER_BIN=${CONTAINER_BIN:-$(which podman)}
CONTAINER_BIN=${CONTAINER_BIN:-$(which docker)}

sudo $CONTAINER_BIN exec lojban_vlasisku bash -c "cd /srv/lojban/vlasisku ; ./manage.py updatedb"
