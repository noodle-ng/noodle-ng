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
        self.host = FTPHost(ip, credentials[0] or "anonymous", credentials[1] or "")
    
    def onewalk(self,dir):
        """Returns a tuple (dirs,files) for the given dir path"""
        dirnames = []
        filenames = []
        
        for entry in self.host.listdir(dir):
            if entry == "." or entry =="..":
                # Skipping . and ..
                continue
            elif self.isdir(self.host.path.join(dir,entry)):
                # Folder
                dirnames.append(entry)
            elif self.isfile(self.host.path.join(dir,entry)):
                # File
                filenames.append(entry)
            else:
                continue
        
        #print (dirnames, filenames)
        return (dirnames, filenames)
    
    def listdir(self,dir):
        return self.host.listdir(dir)
    
    def isdir(self,path):
        return self.host.path.isdir(path)
    
    def isfile(self,path):
        return self.host.path.isfile(path)
    
    def stat(self,path):
        return self.host.stat(path)
