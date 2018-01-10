#!/usr/bin/env python

activate_this = '/home/aburka1/.virtualenvs/vlasisku/bin/activate_this.py'
execfile(activate_this, dict(__file__=activate_this))

import sys
sys.path.insert(0, '/home/aburka1/lojban/vlasisku')

from vlasisku import app as application

