'''
Created on 05.09.2011

@author: moschlar
'''
#TODO: Error handling
#TODO: Docstrings
#TODO: Logging

import logging
from ftputil import FTPHost

#TODO: CleanUp imports
from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit

from crawlerclass.crawler import Crawler

#TODO: Rename type...
type = u"ftp"

log = logging.getLogger(__name__)

class CrawlerFTP(Crawler):
    #TODO: Docstrings
    
    def __init__(self, session, host, username=None, password=None):
        #TODO: Docstrings
        hostname, ip = getHostAndAddr(host)
        if not hasService(ip, type):
            raise Exception("No %s share on %s" % (type, hostname))
        Crawler.__init__(self, type, session, hostname, ip, username, password)
        self.host = FTPHost(ip, username or u"anonymous", password or u"")
    
    def onewalk(self,path):
        """Returns a tuple (dirs,files) for the given dir path"""
        dirnames = []
        filenames = []
        
        try:
            for entry in self.host.listdir(path):
                try:
                    if entry == "." or entry == "..":
                        # Skipping . and ..
                        continue
                    elif self.isdir(self.host.path.join(path, entry)):
                        # Folder
                        dirnames.append(unicode(entry))
                    elif self.isfile(self.host.path.join(path, entry)):
                        # File
                        filenames.append(unicode(entry))
                    else:
                        continue
                except Exception, e:
                    log.debug("Could not analyze %s: %s" % (self.host.path.join(path, entry), e))
                    continue
        #TODO: Error handling
        except Exception, e:
            log.warning("Could not get directory entries in %s: %s" % (path, e))
            raise
        return (dirnames, filenames)
    
    def listdir(self, dir):
        #TODO: Docstrings
        return self.host.listdir(dir)
    
    def isdir(self, path):
        #TODO: Docstrings
        return self.host.path.isdir(path)
    
    def isfile(self, path):
        #TODO: Docstrings
        return self.host.path.isfile(path)
    
    def stat(self, path):
        #TODO: Docstrings
        try:
            return self.host.stat(path)
        except Exception, e:
            log.debug("Could not get stat for %s: %s" % (path, e))
            return (0,0,0,0,0,0,0,0,0,0)
        
