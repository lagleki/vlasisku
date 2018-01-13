#!/usr/bin/env python
#-*- coding:utf-8 -*-

from __future__ import with_statement

from flask.ext.script import Manager

from vlasisku import app
from vlasisku.extensions import database
app.debug = True


manager = Manager(app)


@manager.command
def runbots():
    """Start the IRC bots valsi and gerna."""

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    from vlasisku.irc import GrammarBotFactory, WordBotFactory

    #gerna = GrammarBotFactory(app)
    valsi = WordBotFactory(app)

    log.startLogging(sys.stdout)
    #reactor.connectTCP(gerna.server, gerna.port, gerna)
    reactor.connectTCP(valsi.server, valsi.port, valsi)
    reactor.run()


@manager.shell
def shell_context():

    import pprint

    import flask

    import vlasisku

    context = dict(pprint=pprint.pprint)
    context.update(vars(flask))
    context.update(vars(vlasisku))
    context.update(vars(vlasisku.utils))
    context.update(vars(vlasisku.database))
    context.update(vars(vlasisku.models))

    return context

@manager.command
def updatedb():
    """Export and index a new database from jbovlaste."""

    from contextlib import closing
    import urllib2
    import xml.etree.cElementTree as etree
    import os

    print 'Downloading jbovlaste xml file; this may take a bit.'

    opener = urllib2.build_opener()
    # The bot key is essentially a magic secret for vlasisku and things like
    # it, so you don't have to login with real credentials.  If it stops
    # working, contact the jbovlaste administrator.
    url = 'http://jbovlaste.lojban.org/export/xml-export.html?lang=en&bot_key=z2BsnKYJhAB0VNsl'
    with closing(opener.open(url)) as data:
        print 'Parsing jbovlaste xml'
        xml = etree.parse(data)
        assert xml.getroot().tag == 'dictionary'
        print 'Storing jbovlaste xml'
        with open('vlasisku/data/jbovlaste.xml', 'w') as file:
            xml.write(file, 'utf-8')
        print 'Removing old database.'
        os.system('''
            rm -f vlasisku/data/db.pickle
            touch vlasisku/database.py
            ''')
    print 'The running site should now automatically reload the database, or if it is not running the next startup will do so.'
    # If forcing a reload here is desired, this works: database.init_app(database.app)


if __name__ == "__main__":
    manager.run()
