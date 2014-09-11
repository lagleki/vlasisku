#-*- coding:utf-8 -*-

from __future__ import with_statement

from collections import defaultdict, OrderedDict
import itertools
import re
from functools import wraps
from contextlib import contextmanager
from subprocess import Popen, PIPE
from threading import Thread
from Queue import Queue
import os
import signal

from pqs import Parser
from flask import current_app, request
import jellyfish

def parse_query(query):
    """Parse a search query into a dict mapping fields to lists of match tests.

    >>> parse_query('word:coi')['word']
    ['coi']
    >>> parse_query('coi rodo')['all']
    ['coi', 'rodo']
    >>> parse_query('anythingrandom:foo')['anythingrandom']
    ['foo']
    """
    parsed = defaultdict(list)
    parser = Parser()
    parser.quotechars = set([('"', '"')])
    query = re.sub(r'(\w+?):"', r'"\1:', query)
    for _, token in parser.parse(query):
        if ':' in token:
            field, match = token.split(':', 1)
        else:
            field, match = 'all', token
        parsed[field].append(match)
    return parsed


def unique(iterable):
    """Generator that yields each item only once, in the input order.

    >>> list(unique([1,1,2,2,3,3,2,2,1,1]))
    [1, 2, 3]
    >>> list(unique([3,1,3,2,1,3,2]))
    [3, 1, 2]
    >>> ''.join(unique('A unique string? That does not make much sense!'))
    'A uniqestrg?Thadomkc!'
    """
    seen = set()
    for item in iterable:
        if item not in seen:
            seen.add(item)
            yield item


def compound2affixes(compound):
    """Split a lujvo into rafsi"""
    import vlasisku.zero as zero
    try:
        parts = zero.parse(compound, '', 'expanded_lujvo')[1]
        processed = []
        for i in range(len(parts)):
            if parts[i][-1] == 'y':
                if parts[i][-2] == "'":
                    processed.append(parts[i][:-2])
                    processed.append("'y")
                else:
                    processed.append(parts[i][:-1])
                    processed.append('y')
            elif parts[i][-2:] == "y'":
                processed.append(parts[i][:-2])
                processed.append("y'")
            elif (len(parts[i]) in [4, 5]) and (parts[i][-1] in ['r', 'n']):
                processed.append(parts[i][:-1])
                processed.append(parts[i][-1])
            else:
                processed.append(parts[i])
        return processed
    except:
        return []

def rafsi_lookup(rafsi):
    from vlasisku import database
    if isinstance(rafsi, list):
        return map(rafsi_lookup, filter(lambda r: len(r) > 2, rafsi))

    return (lambda r: (lambda x: x[0].word if len(x) == 1
                                            else r+'?')
                      (filter(lambda e: r in e.searchaffixes,
                              database.root.entries.itervalues())))(rafsi)

def old_compound2affixes(compound):
    """Split a compound word into affixes and glue."""
    c = r'[bcdfgjklmnprstvxz]'
    v = r'[aeiou]'
    cc = r'''(?:bl|br|
                cf|ck|cl|cm|cn|cp|cr|ct|
                dj|dr|dz|fl|fr|gl|gr|
                jb|jd|jg|jm|jv|kl|kr|
                ml|mr|pl|pr|
                sf|sk|sl|sm|sn|sp|sr|st|
                tc|tr|ts|vl|vr|xl|xr|
                zb|zd|zg|zm|zv)'''
    vv = r'(?:ai|ei|oi|au)'
    rafsi3v = r"(?:%(cc)s%(v)s|%(c)s%(vv)s|%(c)s%(v)s'%(v)s)" % locals()
    rafsi3 = r'(?:%(rafsi3v)s|%(c)s%(v)s%(c)s)' % locals()
    rafsi4 = r'(?:%(c)s%(v)s%(c)s%(c)s|%(cc)s%(v)s%(c)s)' % locals()
    rafsi5 = r'%(rafsi4)s%(v)s' % locals()

    for i in xrange(1, len(compound)/3+1):
        reg = r'(?:(%(rafsi3)s)([nry])??|(%(rafsi4)s)(y))' % locals() * i
        reg2 = r'^%(reg)s(%(rafsi3v)s|%(rafsi5)s)$$' % locals()
        matches = re.findall(reg2, compound, re.VERBOSE)
        if matches:
            return [r for r in matches[0] if r]

    return []




def etag(f):
    """Decorator to add ETag handling to a callback."""
    @wraps(f)
    def wrapper(**kwargs):
        if request.if_none_match.contains(current_app.config['ETAG']):
            return current_app.response_class(status=304)
        response = current_app.make_response(f(**kwargs))
        response.set_etag(current_app.config['ETAG'])
        return response
    return wrapper


@contextmanager
def ignore(exc):
    """Context manager to ignore an exception."""
    try:
        yield
    except exc:
        pass


def dameraulevenshtein(seq1, seq2):
    """Calculate the Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Arguments must be strings.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.

    >>> dameraulevenshtein('ba', 'abc')
    2
    >>> dameraulevenshtein('fee', 'deed')
    2
    >>> dameraulevenshtein('abcd', 'bacde')
    3

    Note: the real answer is 2: abcd->bacd->bacde
          but this algorithm is apparently doing abcd->acd->bacd->bacde
    """
    return jellyfish.damerau_levenshtein_distance(seq1.encode('utf-8'),
                                                  seq2.encode('utf-8'))


def jbofihe(text):
    """Call ``jbofihe -ie -cr'' on text and return the output.

    >>> jbofihe('coi rodo')
    "(0[{coi <(1ro BOI)1 do> DO'U} {}])0"
    >>> jbofihe('coi ho')
    Traceback (most recent call last):
      ...
    ValueError: not grammatical: coi _ho_ ⚠
    >>> jbofihe("coi ro do'u")
    Traceback (most recent call last):
      ...
    ValueError: not grammatical: coi ro _do'u_ ⚠
    >>> jbofihe('coi ro')
    Traceback (most recent call last):
      ...
    ValueError: not grammatical: coi ro ⚠
    >>> jbofihe('(')
    Traceback (most recent call last):
      ...
    ValueError: parser timeout
    """
    data = Queue(1)
    process = Popen(('jbofihe', '-ie', '-cr'),
                    stdin=PIPE, stdout=PIPE, stderr=PIPE)

    def target(queue):
        queue.put(process.communicate(text))

    thread = Thread(target=target, args=(data,))
    thread.start()
    thread.join(1)

    if thread.isAlive():
        os.kill(process.pid, signal.SIGTERM)
        raise ValueError('parser timeout')

    output, error = data.get()
    grammatical = not process.returncode # 0=grammatical, 1=ungrammatical

    if grammatical:
        return output.replace('\n', ' ').rstrip()

    error = error.replace('\n', ' ')
    match = re.match(r"^Unrecognizable word '(?P<word>.+?)' "
                     r"at line \d+ column (?P<column>\d+)", error)
    if match:
        reg = r'^(%s)(%s)(.*)' % ('.' * (int(match.group('column')) - 1),
                                  re.escape(match.group('word')))
        text = re.sub(reg, r'\1_\2_ ⚠ \3', text).rstrip()
        raise ValueError('not grammatical: %s' % text)

    if '<End of text>' in error:
        raise ValueError('not grammatical: %s ⚠' % text)

    match = re.search(r'Misparsed token :\s+(?P<word>.+?) \[.+?\] '
                      r'\(line \d+, col (?P<column>\d+)\)', error)
    if match:
        reg = r'^(%s)(%s)(.*)' % ('.' * (int(match.group('column')) - 1),
                                   match.group('word'))
        text = re.sub(reg, r'\1_\2_ ⚠ \3', text).rstrip()
        raise ValueError('not grammatical: %s' % text)

    raise ValueError('not grammatical')

def parse_as(rule, text):
    import vlasisku.zero as zero
    try:
        return zero.parse(text, '', rule)
    except:
        return None

def all_rafsi(word):
    from vlasisku import database
    entry = database.root.query(word)['entry']
    if entry:
        return entry.affixes
    return []

def allowed_pair(pair):
    return (not all(map(lambda c: parse_as("consonant", c), pair))) or parse_as("cluster", pair)

def lujvo_score(lujvo):
    l = len(lujvo)
    a = lujvo.count("'")
    h = lujvo.count("y")
    v = sum(lujvo.count(v) for v in 'aeiou')
    r = 0

    def mapti(r, p):
        p = p.replace('V', '[aeiou]')
        p = p.replace('C', '[bcdfgjklmnprstvxz]')
        p = '^' + p + '$'
        return re.match(p, r) is not None

    for rafsi in parse_as("expanded_lujvo", lujvo)[1]:
        if mapti(rafsi, "CVV[rn]"):
            h += 1
            r += 8
        elif mapti(rafsi, "CV'V[rn]"):
            h += 1
            r += 6
        elif mapti(rafsi, 'CVCCV'):   r += 1
        elif mapti(rafsi, 'CVCCy'):    r += 2
        elif mapti(rafsi, 'CCVCV'):   r += 3
        elif mapti(rafsi, 'CCVCy'):    r += 4
        elif mapti(rafsi, 'CVC'):     r += 5
        elif mapti(rafsi, "CV'V"):    r += 6
        elif mapti(rafsi, 'CCV'):     r += 7
        elif mapti(rafsi, 'CVV'):     r += 8

    return (1000 * l) - (500 * a) + (100 * h) - (10 * r) - v

def jvocuhadju(text, n=4):
    """Build a lujvo from the text (sequence of selrafsi)
    Returns up to n (default 4) possible lujvo as a list of strings, in ascending order by score.

    >>> jvocuhadju('melbi cmalu nixli ckule')
    ["mlecmaxlicu'e", "melcmaxlicu'e", "mlecmanixycu'e", "melcmanixycu'e"]
    >>> jvocuhadju('coi rodo')
    []
    """
    import vlasisku.zero as zero

    selrafsi = text.split(' ')
    for i in range(len(selrafsi)):
        expansion = compound2affixes(selrafsi[i])
        if expansion:
            selrafsi[i] = rafsi_lookup(expansion)
        else:
            selrafsi[i] = [selrafsi[i]]
    selrafsi = sum(selrafsi, [])
    rafsi = OrderedDict()
    for i, sr in zip(range(len(selrafsi)), selrafsi):
        rafsi[sr] = all_rafsi(sr)
        if parse_as("gismu", sr) is not None:
            if i == len(selrafsi)-1:
                rafsi[sr] += [sr]
            else:
                rafsi[sr] += [sr[:-1] + "y"]
        if i == len(selrafsi)-1:
            rafsi[sr] = filter(lambda r: r[-1] in 'aeiou', rafsi[sr])
        else:
            for r in rafsi[sr]:
                if r[-1] in 'aeiou':
                    rafsi[sr] += [r + "r", r + "n"]
        if len(rafsi[sr]) == 0:
            raise ValueError('no appropriate rafsi for %s' % sr)
        else:
            rafsi[sr] = list(set(rafsi[sr]))

    good_lujvo = []
    for lujvo in itertools.product(*rafsi.values()):
        s = lujvo[0]
        for component in lujvo[1:]:
            if allowed_pair(s[-1] + component[0]):
                s += component
            else:
                s += "y" + component

        if parse_as("lujvo", s):
            good_lujvo += [s]


    return sorted(good_lujvo, key=lujvo_score)[:n]

