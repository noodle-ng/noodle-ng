"""Generic filesystem handler

This package defines functions that a filesystem implementation for
noodle must provide to be fully functional for both crawling and 
proxydownloading.

"""

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
    pass

def path_walk(path,visitor,data):
    """Simulate os.path.walk
    
    Callback function visitor will be called with
    (data, dirname, filesindir)
    """
    pass

def stat(path):
    """Get file information (stats)
    
    For the file given by path returns a 10-tuple
    
        mode, ino, dev, nlink, uid, gid, *size, atime, *mtime, *ctime
    
    (Only attributes preceeded with * are currently required, 
    all others may be set 0 if not retrievable)
        
    """
    pass

def open(path):
    """Open file.
    
    Returns file handle specified by path
    """
    pass


