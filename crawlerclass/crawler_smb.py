'''
Created on 05.09.2011

@author: moschlar
'''

import logging
import smbc

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit

from crawlerclass.crawler import Crawler

type = "smb"
smbc_type = {'share': 3, 'folder': 7, 'file': 8}

class CrawlerSMB(Crawler):
    
    def __init__(self, session, host, credentials=None):
        hostname, ip = getHostAndAddr(host)
        if not hasService(ip, type):
            raise Exception("No %s share on %s" % (type, hostname))
        Crawler.__init__(self, type, session, hostname, ip, credentials)
        self.c = smbc.Context()
    
    def uri(self,path):
        return urlUnsplit(type, self.ip, path,self.credentials[0] or None, self.credentials[1] or None)
    
    def onewalk(self,dir):
        """Returns a tuple (dirs,files) for the given
        dir path"""
        dirnames = []
        filenames = []
        #print self.uri(dir)
        try:
            dir = self.c.opendir(self.uri(dir))
            for entry in dir.getdents():
                if entry.name == "." or entry.name =="..":
                    # Skipping . and ..
                    continue
                elif entry.smbc_type == smbc_type['folder'] or entry.smbc_type == smbc_type['share']:
                    # Folder
                    dirnames.append(entry.name.decode())
                elif entry.smbc_type == smbc_type['file']:
                    #File
                    filenames.append(entry.name.decode())
                else:
                    continue
        except:
            pass
        #print (dirnames, filenames)
        return (dirnames, filenames)
    
    def listdir(self,dir):
        (dirnames, filenames) = self.onewalk(dir)
        return dirnames + filenames
    
    def isdir(self,path):
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in dirnames
    
    def isfile(self,path):
        (head, tail) = self.path_split(path)
        (dirnames, filenames) = self.onewalk(head)
        return tail in filenames
    
    def stat(self,path):
        return self.c.open(self.uri(path)).fstat()
