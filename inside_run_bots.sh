#!/bin/bash

function fail {
    echo "$1"
    exit 1
}

(
    flock -n 9 || fail "Lock /tmp/spvlasisku_runbots is being held; exiting."

    echo
    echo "Running bots"
    echo

    cd /srv/lojban/vlasisku/
    export FLASK_APP=vlasisku
    flask runbots
) 9>/tmp/spvlasisku_runbots
