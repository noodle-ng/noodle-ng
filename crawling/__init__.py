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
    """Host is a base class for all implementations of host access methods
    
    Because there are some methods like FTP that require a persistent connection
    to a server I've devided to do this as an object that needs its host information
    at initialization time
    """
    def __init__(self):
        """Initialize the Host object"""
        self.path_split = posixpath.split
        self.path_join = posixpath.join
        self.path_splitext = posixpath.splitext
    
    def path_fullsplit(self, path):
        """Split a given path into its elements"""
        return path.strip(posixpath.sep).split(posixpath.sep)
    
    def onewalk(self, path):
        """Returns a tuple (folders, files) for the directory at the given path
        
        Fail if path is not a directory
        """
        raise NotImplementedError
    
    def listdir(self, path):
        """List directory entries for the given path
        
        Fail if path is not a directory
        """
        raise NotImplementedError
    
    def isdir(self, path):
        """Test if path is a directory"""
        raise NotImplementedError
    
    def isfile(self, path):
        """Test if path is a file"""
        raise NotImplementedError
    
    def stat(self, path):
        """Return a namedtuple stat for the directory entry at path"""
        raise NotImplementedError
    

class Extension():
    """Shall be a base class for crawler extension modules
    
    Extensions can use special function names as hooks during the 
    crawling process
    """
    pass

from crawler import Crawler
from database import DatabaseSession
from smb import SMBHost
host_type = {"smb": SMBHost}
#TODO: Docstring

__all__ = ["Crawler", "DatabaseSession", "Host", "SMBHost"]