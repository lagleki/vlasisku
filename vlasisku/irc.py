#-*- coding:utf-8 -*-

import re

from twisted.internet.protocol import ReconnectingClientFactory
from twisted.python import log
from twisted.words.protocols.irc import IRCClient
from werkzeug import url_quote_plus

from vlasisku import database
from vlasisku.utils import jbofihe, jvocuhadju, compound2affixes, rafsi_lookup

class BotBase(IRCClient):

    def signedOn(self):
        log.msg('* Logged on')
        self.factory.resetDelay()
        for c in self.factory.channels:
            self.join(c)

    # The inherited implementation passes notices to privmsg, causing upset.
    def noticed(self, user, channel, message):
        pass

    def msg(self, target, message):
        log.msg('<%(nickname)s> %(message)s' %
            dict(nickname=self.nickname, message=message))
        IRCClient.msg(self, target, message)

    def privmsg(self, user, channel, message):
        nick = user[:user.index('!')]

        # PM?
        if channel == self.nickname:
            target = nick
            private = True
        else:
            target = channel
            private = False

        query = None
        if target != channel:
            query = message
        else:
            trigger = r'^%(nickname)s[:,]? (?P<query>.+)' \
                    % dict(nickname=re.escape(self.nickname))
            match = re.match(trigger, message)
            if match:
                query = match.group('query')

        if query:
            log.msg('<%(nick)s> %(message)s' % locals())
            self.query(target, query, private)

class FactoryBase(ReconnectingClientFactory):
    server = 'irc.freenode.net'
    port = 6667
    channels = ['#sampre']


class WordBot(BotBase):

    nickname = 'vlaste2'

    def query(self, target, query, private):
        fields = 'affix|rafsi|class|selmaho|type|notes|cll|url|finti|components|lujvo'

        if query == 'help!':
            self.msg(target, '<query http://tiny.cc/query-format > '
                             '[(%s)]' % fields)
            return

        field = 'definition'
        match = re.search(r'\s\((?P<field>%s)\)$' % fields, query)
        if match:
            field = match.group('field')
            query = re.sub(r'\s\(.+?\)$', '', query)

        if field == 'lujvo':
            try:
                lujvos = jvocuhadju(query)
                tanru = query
                query = lujvos[0]
            except ValueError, e:
                self.msg(target, 'error: %s' % e)
                return

        url = 'http://vlasisku.alexburka.com/%s' % url_quote_plus(query)
        results = database.root.query(query)

        entry = results['entry']
        if not entry and len(results['matches']) == 1:
            entry = results['matches'].pop()

        if entry or field in ['components', 'lujvo']:
            case = lambda x: field == x
            if case('definition'):
                data = entry.textdefinition.encode('utf-8')
            elif case('affix') or case('rafsi'):
                data = ', '.join('-%s-' % i for i in entry.affixes)
            elif case('class') or case('selmaho'):
                data = entry.grammarclass
            elif case('type'):
                data = entry.type
            elif case('notes'):
                data = entry.textnotes.encode('utf-8')
            elif case('cll'):
                data = '  '.join(link for (chap, link) in entry.cll)
            elif case('url'):
                data = url
            elif case('finti'):
                data = entry.username
            elif case('components'):
                entry = query
                data = ' '.join(rafsi_lookup(compound2affixes(query)))
            elif case('lujvo'):
                data = ', '.join(lujvos)
                if entry:
                    data += ' (defined as %s = %s)' % (query, entry.textdefinition.encode('utf-8'))
                entry = tanru

            data = data or '(none)'
            if field == 'definition':
                format = '%s = %s'
                self.msg(target, format % (entry, data))
            else:
                format = '%s (%s) = %s'
                self.msg(target, format % (entry, field, data))

        elif results['matches']:
            format = '%d result%s: %s'
            matches = (results['words']
                      +results['glosses']
                      +results['affix']
                      +results['classes']
                      +results['types']
                      +results['definitions']
                      +results['notes'])
            if private:
                data = ', '.join(map(str, matches))
            else:
                data = ', '.join(map(str, matches[:10]))
                if len(results['matches']) > 10:
                    data += '…'
            self.msg(target, format % (len(results['matches']),
                                       's' if len(results['matches']) != 1
                                           else '',
                                       data))
        else:
            if field not in ['components', 'lujvo']:
                try:
                    rafsi = compound2affixes(query)
                    if len(rafsi) > 0:
                        tanru = [e.word for a in rafsi
                                        if len(a) != 1
                                        for e in database.root.entries.itervalues()
                                        if a in e.searchaffixes]
                        lujvo = jvocuhadju(' '.join(tanru))[0]
                        if lujvo != query:
                            if field != 'definition':
                                return self.query(target, '%s (%s)' % (lujvo, field), private)
                            else:
                                return self.query(target, lujvo, private)
                except:
                    pass
            self.msg(target, 'no results. %s' % url)

class WordBotFactory(FactoryBase):
    protocol = WordBot

class GrammarBot(BotBase):

    nickname = 'tcepru2'

    def query(self, target, query):
        try:
            response = yaccparser(query)
        except ValueError, e:
            response = str(e)

        self.msg(target, response)

class GrammarBotFactory(FactoryBase):
    protocol = GrammarBot
