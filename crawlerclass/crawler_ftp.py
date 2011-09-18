'''
Created on 05.09.2011

@author: moschlar
'''

import logging
from ftputil import FTPHost

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit

from crawlerclass.crawler import Crawler

type = "ftp"

class CrawlerFTP(Crawler):
    
    def __init__(self, session, host, credentials=None):
        hostname, ip = getHostAndAddr(host)
        if not hasService(ip, type):
            raise Exception("No %s share on %s" % (type, hostname))
        Crawler.__init__(self, type, session, hostname, ip, credentials)
        self.host = FTPHost(ip, credentials[0] or u"anonymous", credentials[1] or "")
    
    def onewalk(self,path):
        """Returns a tuple (dirs,files) for the given dir path"""
        dirnames = []
        filenames = []
        
        try:
            for entry in self.host.listdir(path):
                try:
                    if entry == "." or entry =="..":
                        # Skipping . and ..
                        continue
                    elif self.isdir(self.host.path.join(path,entry)):
                        # Folder
                        dirnames.append(unicode(entry))
                    elif self.isfile(self.host.path.join(path,entry)):
                        # File
                        filenames.append(unicode(entry))
                    else:
                        continue
                except Exception, e:
                    logging.debug("Could not evaluate %s: %s" % (self.host.path.join(path,entry), e))
                    continue
        except Exception, e:
            logging.debug("Could not get directory entries in %s: %s" % (path, e))
            pass
        return (dirnames, filenames)
    
    def listdir(self,dir):
        return self.host.listdir(dir)
    
    def isdir(self,path):
        return self.host.path.isdir(path)
    
    def isfile(self,path):
        return self.host.path.isfile(path)
    
    def stat(self,path):
        try:
            return self.host.stat(path)
        except Exception, e:
            logging.debug("Could not get stat for %s: %s" % (path, e))
            return (0,0,0,0,0,0,0,0,0,0)
        
