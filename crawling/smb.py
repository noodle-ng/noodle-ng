'''
Created on 21.09.2011

@author: moschlar
'''
#TODO: Docstring

import logging
import smbc

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit

from . import stat, Host

log = logging.getLogger("SMBHost")

smbc_type = {'share': 3, 'folder': 7, 'file': 8}
#TODO: Docstring

class SMBHost(Host):
    #TODO: Docstring
    
    type = u"smb"
    
    def __init__(self, host, username=None, password=None):
        #TODO: Docstring
        Host.__init__(self)
        hostname, ip = getHostAndAddr(host)
        if not ip:
            raise Exception("Host %s not reachable" % (host))
        if not hasService(ip, self.type):
            raise Exception("No %s service on %s" % (self.type, hostname))
        self.hostname = hostname
        self.ip = ip
        self.username = username
        self.password = password
        self.c = smbc.Context()
    
    def uri(self, path):
        #TODO: Docstrings
        return urlUnsplit(self.type, self.ip, path, self.username or None, self.password or None).encode(encoding="utf-8")
    
    def onewalk(self, path):
        #TODO: Docstring
        dirnames = []
        filenames = []
        
        try:
            for entry in self.c.opendir(self.uri(path)).getdents():
                if entry.name == "." or entry.name == ".." or \
                    entry.name.endswith("$"):
                    #entry.name == "print$" or entry.name == "IPC$": \
                    # Skipping . and ..
                    continue
                elif entry.smbc_type == smbc_type['share']:
                    # Share
                    try:
                        subpath = self.uri(self.path_join(path, entry.name))
                        self.c.opendir(subpath)
                    except smbc.PermissionError as e:
                        log.info("Could not access share %s: %s" % (subpath, e))
                        continue
                    else:
                        dirnames.append(unicode(entry.name, encoding="utf-8"))
                elif entry.smbc_type == smbc_type['folder']:
                    # Folder
                    dirnames.append(unicode(entry.name, encoding="utf-8"))
                elif entry.smbc_type == smbc_type['file']:
                    # File
                    filenames.append(unicode(entry.name, encoding="utf-8"))
                else:
                    continue
        except smbc.PermissionError as e:
            log.info(e)
            pass
        except smbc.NoEntryError as e:
            log.info(e)
            pass
        #TODO: Error handling
        except Exception as e:
            log.warning("Could not get directory entries in %s: %s" % (self.uri(path), e))
            raise
        return (dirnames, filenames)
    
    def listdir(self, dir):
        #TODO: Docstrings
        (dirnames, filenames) = self.onewalk(dir)
        return dirnames + filenames
    
    def isdir(self, path):
        #TODO: Docstring
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in dirnames
    
    def isfile(self, path):
        #TODO: Docstring
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in filenames
    
    def stat(self, path):
        #TODO: Docstrings
        try:
            return stat(*self.c.stat(self.uri(path)))
        except Exception as e:
            #TODO: Error handling
            log.info("Could not get stat for %s: %s" % (self.uri(path), e))
            return stat(0,0,0,0,0,0,0,0,0,0)
    
