"""Samba filesystem handler

This module provides functions to handle standard filesystem operations
like the os-module but for samba shares.
Therefor an actual version of pysmbc is needed.

"""

from smbc import Context
from urlparse import urlparse

# smbc type shortcuts
smbc_type = {'share': 3, 'folder': 7, 'file': 8}

c = Context()

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

    dirpath = urlparse(top).path
    dirnames = []
    filenames = []
    
    dir = c.opendir(top)
    direntries = dir.getdents()
    for entry in direntries:
        if entry.name == "." or entry.name =="..":
            #print "skip"
            # Skipping . and ..
            continue
        elif entry.smbc_type == smbc_type['folder']:
            #print "folder %s" % entry.name
            # Folder
            dirnames.append(entry.name)
        elif entry.smbc_type == smbc_type['file']:
            #print "file %s" % entry.name
            #File
            filenames.append(entry.name)
        else:
            continue
    
    #print (dirpath, dirnames, filenames)
    yield (dirpath, dirnames, filenames)
    
    for dirname in dirnames:
        #print "dirname: %s" % dirname
        newpath = top + "/" + dirname
        #print "newpath: %s" % newpath
        for dir in walk(newpath):
            yield dir

def path_walk(path,visitor,data):
    """Simulate os.path.walk
    
    Callback function visitor will be called with
    (data, dirname, filesindir)
    """
    
    for (dirpath, dirnames, filenames) in walk(path):
        visitor(data, dirpath, dirnames + filenames)
    return

def stat(path):
    """Get file information (stats)
    
    For the file given by path returns a 10-tuple
    
        mode, ino, dev, nlink, uid, gid, *size, atime, *mtime, *ctime
    
    (Only attributes preceeded with * are currently required, 
    all others may be set 0 if not retrievable)
        
    """
    
    return c.open(path).fstat()

def open(path):
    """Open file.
    
    Returns file handle specified by path
    """
    
    return c.open(path)
