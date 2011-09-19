'''
Created on 05.09.2011

@author: moschlar
'''

import logging
import smbc
"""I advise you to use pysmbc==1.0.9, since other versions may not work reliable!"""

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit

from crawlerclass.crawler import Crawler

type = u"smb"
smbc_type = {'share': 3, 'folder': 7, 'file': 8}

log = logging.getLogger(__name__)

class CrawlerSMB(Crawler):
    
    def __init__(self, session, host, username=None, password=None):
        hostname, ip = getHostAndAddr(host)
        if not hasService(ip, type):
            raise Exception("No %s share on %s" % (type, hostname))
        Crawler.__init__(self, type, session, hostname, ip, username, password)
        self.c = smbc.Context()
    
    def uri(self, path):
        return urlUnsplit(type, self.ip, path, self.username or None, self.password or None).encode(encoding="utf-8")
    
    def onewalk(self, path):
        """Returns a tuple (dirs,files) for the given dir path"""
        dirnames = []
        filenames = []
        
        try:
            for entry in self.c.opendir(self.uri(path)).getdents():
                if entry.name == "." or entry.name == "..":
                    # Skipping . and ..
                    continue
                elif entry.smbc_type == smbc_type['folder'] or entry.smbc_type == smbc_type['share']:
                    # Folder
                    dirnames.append(unicode(entry.name, encoding="utf-8"))
                elif entry.smbc_type == smbc_type['file']:
                    # File
                    filenames.append(unicode(entry.name, encoding="utf-8"))
                else:
                    continue
        #TODO: More specific Error Handling
        except smbc.PermissionError:
            pass
        except Exception, e:
            log.debug("Could not get directory entries in %s: %s" % (self.uri(path), e))
            raise
        return (dirnames, filenames)
    
    def listdir(self, dir):
        (dirnames, filenames) = self.onewalk(dir)
        return dirnames + filenames
    
    def isdir(self, path):
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in dirnames
    
    def isfile(self, path):
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in filenames
    
    def stat(self, path):
        try:
            return self.c.open(self.uri(path)).fstat()
        except Exception, e:
            log.debug("Could not get stat for %s: %s" % (self.uri(path), e))
            return (0,0,0,0,0,0,0,0,0,0)
