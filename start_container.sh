#!/bin/bash

set -x

/srv/lojban/vlasisku/manage.py updatedb

# Even if updatedb fails, we want to try to run anyway with the
# previous data
/srv/lojban/vlasisku/manage.py runserver -h 0.0.0.0 -p 8080 --threaded --passthrough-errors -D -r
