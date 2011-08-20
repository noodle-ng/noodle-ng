"""FTP filesystem handler

This module provides functions to handle standard filesystem operations
like the os-module but for remote ftp servers

"""

from ftputil import FTPHost
from urlparse import urlparse

def parseuri(uri):
    url = urlparse(uri)
    user = url.username or "anonymous"
    password = url.password or ""
        
    return (url.hostname,url.path,user,password)

def walk(top):
    """Directory tree generator.

    For each directory in the directory tree rooted at top (including top
    itself, but excluding '.' and '..'), yields a 3-tuple

        dirpath, dirnames, filenames

    dirpath is a string, the path to the directory.  dirnames is a list of
    the names of the subdirectories in dirpath (excluding '.' and '..').
    filenames is a list of the names of the non-directory files in dirpath.
    Note that the names in the lists are just names, with no path components.
    To get a full path (which begins with top) to a file or directory in
    dirpath, do os.path.join(dirpath, name).
    """
    
    (hostname,path,user,password) = parseuri(top)
    host = FTPHost(hostname,user,password)
    
    for dir in host.walk(path):
        yield dir

def path_walk(path,visitor,data):
    """Simulate os.path.walk
    
    Callback function visitor will be called with
    (data, dirname, filesindir)
    """
    
    for (dirpath, dirnames, filenames) in walk(path):
        visitor(data, dirpath, dirnames + filenames)
    return

def stat(top):
    """Get file information (stats)
    
    For the file given by path returns a 10-tuple
    
        mode, ino, dev, nlink, uid, gid, *size, atime, *mtime, *ctime
    
    (Only attributes preceeded with * are currently required, 
    all others may be set 0 if not determinable)
        
    """
    
    (hostname,path,user,password) = parseuri(top)
    host = FTPHost(hostname,user,password)
    
    return host.stat(path)

def fopen(top):
    """Open file.
    
    Returns file handle specified by path
    """
    
    (hostname,path,user,password) = parseuri(top)
    host = FTPHost(hostname,user,password)
    
    return host.open(path)
