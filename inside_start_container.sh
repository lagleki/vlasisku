#!/bin/bash

set -x

cd /srv/lojban/vlasisku/
export FLASK_APP=vlasisku
flask updatedb

# Even if updatedb fails, we want to try to run anyway with the
# previous data
gunicorn vlasisku:app --access-logfile - --error-logfile - --access-logformat '%(h)s %({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"' -w 1 -b 0.0.0.0:8080
