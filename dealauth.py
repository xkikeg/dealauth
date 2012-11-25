#!/usr/bin/env python3

import os, sys
import subprocess
from io import StringIO

import genauthkeys
from optparse import OptionParser
from genauthkeys import GenAuthKeys, getHostFromPublicKeyFile


RSYNC_COMMAND = """rsync -a --itemize-changes --checksum --rsh='ssh -o "ConnectTimeout=10"' --backup --suffix=.bak --delay-updates"""

SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_KEY_DIR_NAME = "pubkey.d"

USAGE = """%prog [options]... [hosts]..."""

def defaultGet(default, x):
    return x if x is not None else default


def rsync_itemize_is_sended(result):
    return result[0] == '<'


class DealAuthApp(object):
    def __init__(self, key_dir=None, tmp_dir=None):
        KEY_DIR = defaultGet(
            os.path.join(SCRIPT_DIR, DEFAULT_KEY_DIR_NAME), key_dir)
        TMP_DIR = defaultGet(os.path.join(KEY_DIR, "tmp/"), tmp_dir)
        os.path.isdir(TMP_DIR) or os.mkdir(TMP_DIR)
        self.KEY_DIR = KEY_DIR
        self.TMP_DIR = TMP_DIR

    def updateKey(self, host, group):
        TMP_DIR = self.TMP_DIR
        rsynccommandline = " ".join((RSYNC_COMMAND,
                                     os.path.join(TMP_DIR, group + ".auth"),
                                     host + ":.ssh/authorized_keys"))
        status, output = subprocess.getstatusoutput(rsynccommandline)
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
        os.chmod(authfile, 0o600)


def main():
    parser = OptionParser(USAGE)
    parser.add_option("-k", "--key-dir", dest="key_dir",
                      help="directory containing public keys")
    parser.add_option("-t", "--tmp-dir", dest="tmp_dir",
                      help="directory containing temporary authfiles")

    option, args = parser.parse_args()

    app = DealAuthApp(**vars(option))

    g = GenAuthKeys(app.KEY_DIR)

    if len(args) != 0:
        try:
            groups = g.findGroups(args)
        except genauthkeys.NotFoundHostException as inst:
            print("%s is invalid host name." % str(inst), file=sys.stderr)
            sys.exit(2)
        for gr in set(groups):
            app.mkAuthFile(g, gr)
        for ho, gr in zip(args, groups):
            app.updateKey(ho, gr)
        return

    for group in g.groups():
        app.mkAuthFile(g, group)
        app.updateGroupKeys(group)


if __name__ == "__main__":
    main()
