# Copyright the Karmabot authors and contributors.
# All rights reserved.  See AUTHORS.
#
# This file is part of 'karmabot' and is distributed under the BSD license.
# See LICENSE for more details.
from __future__ import print_function

import sys
import os.path
import re
import time
from twisted.python import log

import karmabot.client as karmabot
from karmabot.facets import (
    bot,
    karma,
    description,
    name,
    help,
    irc as ircfacet,
    )

#XXX:dc:whats this for?
sys.path.append("../src")

# Designed to parse bip logs (http://bip.t1r.net)
LOG_RE = re.compile(
    r"(?P<when>[\d-]+\s*[\d:]+)\s*<\s*(?P<user>[^:]+): (?P<msg>.*)")


def reincarnate(bot, path):
    with open(path) as f:
        channel = os.path.basename(path).split(".")[0]
        for line in f:
            m = LOG_RE.match(line)
            if m:
                when = time.mktime(time.strptime(m.group("when"),
                                                 "%d-%m-%Y %H:%M:%S"))

                # Bwahahahaha.
                _time = time.time
                time.time = lambda: when
                try:
                    bot.privmsg(m.group("user"), channel, m.group("msg"))
                except Exception:
                    log.err()
                finally:
                    time.time = _time


class ImaginaryKarmaBotFactory(object):
    def __init__(self, nick, filename):
        self.nick = nick
        self.channels = None
        self.filename = filename
        self.trusted = None
        self.password = None


def main():
    from optparse import OptionParser
    parser = OptionParser(usage="usage: %prog [options]")

    parser.add_option("-v", "--verbose",
                      action="store_true", dest="verbose", default=False,
                      help="enable verbose output")
    parser.add_option("-d", "--data",
                      action="store", dest="filename", default="karma.json",
                      help="karma data file name")
    parser.add_option("-n", "--nick",
                      action="store", dest="nick", default="karmabot",
                      help="nickname to use")
    parser.add_option("-f", "--facets",
                      action="append", dest="facets", default=[],
                      help="additional facets to load")

    (options, paths) = parser.parse_args()

    if options.verbose:
        log.startLogging(sys.stdout)

    # FIXME: this needs to be replaced with a real facet manager
    for facet_path in options.facets:
        execfile(facet_path, globals())

    kb = karmabot.KarmaBot()
    kb.factory = ImaginaryKarmaBotFactory(options.nick, options.filename)

    kb.init()
    kb.nickname = options.nick

    # You have no mouth, no legs.
    kb.msg = kb.join = kb.leave = lambda *x: None

    # My life is flashing before my eyes...
    for path in paths:
        reincarnate(kb, path)

    kb.save()

if __name__ == "__main__":

    main()
