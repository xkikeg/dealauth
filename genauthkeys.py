#!/usr/bin/env python

import os, sys
import re
from ConfigParser import SafeConfigParser

DEFAULT_CONFIG_FILE_NAME = "dealauth.conf"

GIT_PREFIX = r'command="git shell -c \"$SSH_ORIGINAL_COMMAND\"" '
SVN_PREFIX = r'command="if [ \"svnserve -t\" != \"$SSH_ORIGINAL_COMMAND\" ];then echo not allowed to login.; exit 2; fi; svnserve -t" '
VCS_PREFIX = r'command="${HOME}/local/bin/ssh-limiter --all \"$SSH_ORIGINAL_COMMAND\"" '


class NotFoundHostException(Exception):
    pass


class AllowGroup(object):

    """Class to represent allowed group."""

    pattern_limit_host = re.compile("(.*?)\[(.*?)\]")

    def __init__(self, group):
        self.group = group

    def __str__(self):
        return self.__class__.__name__ + "('"+ self.group +"')"

    def mkauth(self, KEY_DIR):
        allow = self.group
        m = self.pattern_limit_host.match(allow)
        limited_hosts = None
        if m:
            allow = m.group(1)
            limited_hosts = set(m.group(2).split(","))
        outstr = ""
        for path, dirs, files in os.walk(os.path.join(KEY_DIR, allow)):
            for fname in files:
                # If not a public key.
                is_pubkey, host = getHostFromPublicKeyFile(fname)
                if not is_pubkey: continue
                # If not included in limitation and limitation exists.
                if limited_hosts and not host in limited_hosts: continue
                f = open(os.path.join(path, fname), "r")
                outstr += self.decorate(f.read())
        return outstr

    def decorate(self, string):
        return string


class GitAllowGroup(AllowGroup):

    """Class to represent allowed group only to use Git."""

    def decorate(self, string):
        return GIT_PREFIX + string


class SvnAllowGroup(AllowGroup):

    """Class to represent allowed group only to use subversion."""

    def decorate(self, string):
        return SVN_PREFIX + string


class VcsAllowGroup(AllowGroup):

    """Class to represent allowed group only to use version control system."""

    def decorate(self, string):
        return VCS_PREFIX + string


def isMatchPublicKeyFile(f):
    return f.endswith(".pub")


def getHostFromPublicKeyFile(f):
    if not f.endswith(".pub"):
        return (False, None)
    return (True, f[:-4])


def findGroup(KEY_DIR, host):
    for path, dirs, files in os.walk(KEY_DIR):
        for f in files:
            if f == host+".pub":
                return os.path.basename(path)
    return None


class GenAuthKeys(object):
    def __init__(self, key_dir, configfile=None):
        self.KEY_DIR = key_dir
        if configfile is None:
            configfile = os.path.join(key_dir, DEFAULT_CONFIG_FILE_NAME)
        config = SafeConfigParser()
        config.read(configfile)
        self.config = config

    def findGroups(self, hosts):
        ret = [findGroup(self.KEY_DIR, h) for h in hosts]
        for i, x in enumerate(ret):
            if x is None:
                raise NotFoundHostException(hosts[i])
        return ret

    def groups(self):
        return self.config.sections()

    def isAllowSelf(self, group):
        if not self.config.has_option(group, "AllowSelf"):
            return True
        return self.config.getboolean(group, "AllowSelf")

    def genAuth(self, group, output=sys.stdout):
        config = self.config
        # Not existing group
        if not config.has_section(group):
            pass
        # allowed group
        allows = [AllowGroup(i) for i in config.get(group, "Allow").split()]
        if self.isAllowSelf(group):
            allows += [AllowGroup(group)]
        if config.has_option(group, "GitAllow"):
            allows += [GitAllowGroup(i) for i in config.get(group, "GitAllow").split()]
        if config.has_option(group, "SvnAllow"):
            allows += [SvnAllowGroup(i) for i in config.get(group, "SvnAllow").split()]
        if config.has_option(group, "VcsAllow"):
            allows += [VcsAllowGroup(i) for i in config.get(group, "VcsAllow").split()]
        for allow in allows:
            output.write(allow.mkauth(self.KEY_DIR))


if __name__ == "__main__":
    _x = GenAuthKeys()
    if len(sys.argv) < 2:
        target = ("eccs", )
    else:
        target = sys.argv[1:]
    for i in target:
        _x.genAuth(i)
    pass
