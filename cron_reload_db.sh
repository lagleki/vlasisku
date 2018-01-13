#!/bin/sh

sudo docker exec lojban_vlasisku bash -c "cd /srv/lojban/vlasisku ; ./manage.py updatedb"
