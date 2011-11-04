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
    """SMBHost is a class for smb connections to hosts
    
    It makes heavy usage of pysmbc methods.
    """
    
    type = u"smb"
    
    def __init__(self, host, username=None, password=None):
        """Initialize the SMBHost object
        
        host can be an ip address or a hostname, any of it will be resolved, if possible
        if username and passwort are not set, anonymous access will be tried
        """
        
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
        """Generates an uri for the given path, based on the objects host, username and password"""
        return urlUnsplit(self.type, self.ip, path, self.username or None, self.password or None).encode(encoding="utf-8")
    
    def onewalk(self, path):
        """Returns a tuple (folders, files) for the directory at the given path"""
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
        #TODO: Should return namedtuple onewalk like stat does
        return (dirnames, filenames)
    
    def listdir(self, dir):
        """List directory entries for the given path"""
        (dirnames, filenames) = self.onewalk(dir)
        return dirnames + filenames
    
    def isdir(self, path):
        """Test if path is a directory"""
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in dirnames
    
    def isfile(self, path):
        """Test if path is a file"""
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in filenames
    
    def stat(self, path):
        """Return a namedtuple stat for the directory entry at path"""
        try:
            return stat(*self.c.stat(self.uri(path)))
        except Exception as e:
            #TODO: Error handling
            log.info("Could not get stat for %s: %s" % (self.uri(path), e))
            return stat(0,0,0,0,0,0,0,0,0,0)
    
