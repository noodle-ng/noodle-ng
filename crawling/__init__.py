'''
Created on 21.09.2011

@author: moschlar
'''
#BETA BETA BETA BETA BETA BETA BETA BETA BETA BETA
#TODO: Docstring

import posixpath
from collections import namedtuple

stat = namedtuple("stat", ["mode","ino","dev","nlink","uid","gid","size","atime","mtime","ctime"])
#TODO: Docstring
onewalk = namedtuple("stat", ["mode","ino","dev","nlink","uid","gid","size","atime","mtime","ctime"])
#TODO: Docstring

class HostNotReachableException(Exception):
    pass

class NoServiceException(Exception):
    pass

class Host():
    #TODO: Docstring
    def __init__(self):
        #TODO: Docstring
        self.path_split = posixpath.split
        self.path_join = posixpath.join
        self.path_splitext = posixpath.splitext
    
    def path_fullsplit(self, path):
        #TODO: Docstring
        return path.strip(posixpath.sep).split(posixpath.sep)
    
    def onewalk(self, path):
        #TODO: Docstring
        raise NotImplementedError
    def listdir(self, path):
        #TODO: Docstringcrawl
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
#TODO: Docstring

__all__ = ["Crawler", "DatabaseSession", "Host", "SMBHost"]