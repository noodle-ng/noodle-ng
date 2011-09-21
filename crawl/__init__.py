'''
Created on 21.09.2011

@author: moschlar
'''
#TODO: Docstring

from collections import namedtuple

stat = namedtuple("stat", ["mode","ino","dev","nlink","uid","gid","size","atime","mtime","ctime"])
#TODO: Docstring

class HostNotReachableException(Exception):
    pass

class NoServiceException(Exception):
    pass

class Host():
    #TODO: Docstring
    
    def __init__(self):
        #TODO: Docstring
        raise NotImplementedError
    def onewalk(self, path):
        #TODO: Docstring
        raise NotImplementedError
    def listdir(self, path):
        #TODO: Docstring
        raise NotImplementedError
    def isdir(self, path):
        #TODO: Docstring
        raise NotImplementedError
    def isfile(self, path):
        #TODO: Docstring
        raise NotImplementedError
    def stat(self, path):
        #TODO: Docstring
        raise NotImplementedError

class Extension():
    #TODO: Docstring
    pass

from crawler import Crawler
from database import DatabaseSession
from smb import SMBHost

host_type = {"smb": SMBHost}

__all__ = ["Crawler", "DatabaseSession", "Host", "SMBHost"]