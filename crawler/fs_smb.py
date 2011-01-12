"""Generic filesystem handler

This package defines functions that a filesystem implementation for
noodle must provide to be fully functional for both crawling and 
proxydownloading.

"""

import smbc
# smbc type shortcuts
smbc_type = {'share':3, 'folder':7, 'file':8}

c = smbc.Context()

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

    dirpath = top
    dirnames = []
    filenames = []
    
    dir = c.opendir(dirpath)
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
        newpath = dirpath+"/"+dirname
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
#    print c.open("smb://localhost/downloads/BspKlausurAufg.pdf").fstat()
#    (33188, 468894, 0, 4032, 0, 1, 1000, 1000, 60006, 0)
#    vs.
#    os.stat("/home/moschlar/Downloads/BspKlausurAufg.pdf")
#    posix.stat_result(st_mode=33188, st_ino=393329L, st_dev=2054L, st_nlink=1, st_uid=1000, st_gid=1000, st_size=60006L, st_atime=1294817044, st_mtime=1294817013, st_ctime=1294817013)

    try:
        fstat = c.open(path).fstat()
        #print fstat
    except:
        fstat = (0,0,0,0,0,0,0,0,0,0)
    
    return (0,0,0,0,fstat[6],fstat[7],fstat[8],0,0,0)

def open(path):
    """Open file.
    
    Returns file handle specified by path
    """
    
    f = c.open(path)
    return f
