#!/bin/bash

cd /srv/lojban/vlasisku/
export FLASK_APP=vlasisku
flask updatedb
