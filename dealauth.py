#!/usr/bin/env python

from __future__ import print_function

import os, sys
from commands import getstatusoutput
from cStringIO import StringIO

import genauthkeys
from argparse import ArgumentParser
from genauthkeys import GenAuthKeys, getHostFromPublicKeyFile

RSYNC_COMMAND = """rsync -a --itemize-changes --checksum --rsh='ssh -o "ConnectTimeout=10"' --backup --suffix=.bak --delay-updates"""

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))

DEFAULT_KEY_DIR_NAME = "pubkey.d"
DEFAULT_TMP_DIR_NAME = os.path.join(DEFAULT_KEY_DIR_NAME, "tmp")
DEFAULT_KEY_DIR = os.path.join(SCRIPT_DIR, DEFAULT_KEY_DIR_NAME)
DEFAULT_TMP_DIR = os.path.join(SCRIPT_DIR, DEFAULT_TMP_DIR_NAME)

def defaultGet(default, x):
    return x if x is not None else default


def rsync_itemize_is_sended(result):
    return result[0] == '<'


class DealAuthApp(object):
    def __init__(self, KEY_DIR, TMP_DIR):
        os.path.isdir(TMP_DIR) or os.mkdir(TMP_DIR)
        self.KEY_DIR = KEY_DIR
        self.TMP_DIR = TMP_DIR

    def updateKey(self, host, group):
        TMP_DIR = self.TMP_DIR
        rsynccommandline = " ".join((RSYNC_COMMAND,
                                     os.path.join(TMP_DIR, group + ".auth"),
                                     host + ":.ssh/authorized_keys"))
        status, output = getstatusoutput(rsynccommandline)
        if status != 0:
            print('=== error: '+host+' ===')
            print(output)
            return False
        if output == "" or not rsync_itemize_is_sended(output):
            print('not updated: "'+host+'"')
        else:
            print('update completed: "'+host+'"')
        return True

    def updateGroupKeys(self, group):
        for path, dirs, files in os.walk(os.path.join(self.KEY_DIR, group)):
            for fname in files:
                is_pubkey, host = getHostFromPublicKeyFile(fname)
                if is_pubkey:
                    success = self.updateKey(host, group)

    def mkAuthFile(self, genkey, group):
        authfile = os.path.join(self.TMP_DIR, group+".auth")
        fnew = StringIO()
        genkey.genAuth(group, fnew)
        if os.path.isfile(authfile):
            oldf = open(authfile, "r")
            oldauth = oldf.read()
            oldf.close()
        else:
            oldauth = ""
        newauth = fnew.getvalue()
        if oldauth != newauth:
            f = open(authfile, "w")
            f.write(newauth)
            f.close()
        os.chmod(authfile, 0600)


def main():
    parser = ArgumentParser(description="Generate & maintain authorized_keys above all nodes")
    parser.add_argument("-k", "--key-dir",
                        default=DEFAULT_KEY_DIR_NAME,
                        help="directory containing public keys (default: %(default)s)")
    parser.add_argument("-t", "--tmp-dir",
                        default=DEFAULT_TMP_DIR_NAME,
                        help="directory containing temporary authfiles (default: %(default)s)")
    parser.add_argument("hosts", nargs="*",
                        help="Hosts to update authorized_keys")

    args = parser.parse_args()
    app = DealAuthApp(args.key_dir, args.tmp_dir)
    g = GenAuthKeys(app.KEY_DIR)
    hosts = args.hosts

    if len(hosts) != 0:
        try:
            groups = g.findGroups(hosts)
        except genauthkeys.NotFoundHostException as inst:
            print("%s is invalid host name." % str(inst), file=sys.stderr)
            sys.exit(2)
        for gr in set(groups):
            app.mkAuthFile(g, gr)
        for ho, gr in zip(hosts, groups):
            app.updateKey(ho, gr)
        return

    for group in g.groups():
        app.mkAuthFile(g, group)
        app.updateGroupKeys(group)


if __name__ == "__main__":
    main()
