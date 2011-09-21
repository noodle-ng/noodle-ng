'''
Created on 21.09.2011

@author: moschlar
'''

import logging, time, posixpath
from datetime import datetime

from noodle.model.share import Folder, File

log = logging.getLogger("Crawler")

class Crawler():
    #TODO: Docstring
    
    def __init__(self, databasesession, host, extension=None):
        #TODO: Docstring
        self.path_split = posixpath.split
        self.path_join = posixpath.join
        self.path_splitext = posixpath.splitext
        
        self.db = databasesession
        self.host = host
        self.extension = extension
    
    def walker(self, database_dir, host_dir):
        #TODO: Docstring
        
        log.debug("Started crawling %s" % host_dir)
        
        # Variables for tracking statistics
        sizesum = newsum = updsum = delsum = 0
        
        # Get lists for host and database
        host_folders, host_files = self.host.onewalk(host_dir)
        db_folders, db_files = database_dir.childDict
        
        #log.debug("host_list: %s %s" % (str(host_folders), str(host_files)))
        #log.debug("database_list: %s %s" % (str(db_folders), str(db_files)))
        
        # We use sets here because we can perform union, intersection and complement operations on them
        newFiles = set(f for f in host_files) - set(f for f in db_files)
        newFolders = set(f for f in host_folders) - set(f for f in db_folders)
        
        updateFiles = set(f for f in host_files) & set(f for f in db_files)
        updateFolders = set(f for f in host_folders) & set(f for f in db_folders)
        
        delFiles = set(f for f in db_files) - set(f for f in host_files)
        delFolders = set(f for f in db_folders) - set(f for f in host_folders)
        
        for newFile in newFiles:
            log.debug("New: %s" % newFile)
            newsum += 1
            name, ext = self.path_splitext(newFile)
            stat = self.host.stat(self.path_join(host_dir, newFile))
            file = File(name, ext)
            file.name = name
            file.extension = ext
            file.size = stat.size
            sizesum += file.size
            file.date = datetime.fromtimestamp(stat.mtime)
            file.last_update = datetime.now()
            database_dir.children.append(file)
        
        for updateFile in updateFiles:
            log.debug("Update: %s" % updateFile)
            #name, ext = self.path_splitext(updateFile) # won't change, because it wouldn't be the same file then
            stat = self.host.stat(self.path_join(host_dir, updateFile))
            file = db_files[updateFile]
            if file.size != stat.size or file.date != datetime.fromtimestamp(stat.mtime):
                log.debug("   Changed: %s" % updateFile)
                updsum += 1
                file.size = stat.size
                file.date = datetime.fromtimestamp(stat.mtime)
                file.last_update = datetime.now()
            sizesum += file.size
        
        for delFile in delFiles:
            log.debug("Delete: %s" % delFile)
            delsum += 1
            try:
                del database_dir.children[database_dir.children.index(delFile)]
            except Exception,e:
                log.warning("Could not delete %s from database: %s" % (delFile, e))
            del db_files[delFile]
        
        for newFolder in newFolders:
            log.debug("New: %s" % newFolder)
            newsum += 1
            folder = Folder(newFolder)
            folder.last_update = datetime.now()
            database_dir.children.append(folder)
            db_folders[newFolder] = folder
        
        for updateFolder in updateFolders:
            log.debug("Update: %s" % updateFolder)
            pass
            updsum += 1
            # TODO: Not sure what to do here, since we mostly can't get stats from a directory
            # - We could set its size to the sum of its contents
            # - We could set its last_update when any of its children changes
            folder = db_folders[updateFolder]
            folder.last_update = datetime.now()
        
        for delFolder in delFolders:
            log.debug("Delete: %s" % delFolder)
            delsum += 1
            try:
                # Sometimes there were errors about an item not being in the list
                del database_dir.children[database_dir.children.index(delFolder)]
            except Exception,e:
                log.warning("Could not delete %s from database: %s" % (delFile, e))
            del db_folders[delFolder]
        
        
        # Perform recursive walking and sum up the stats
        for folder in db_folders.itervalues():
            size, new, updated, deleted = self.walker(folder,self.path_join(host_dir, folder.name))
            sizesum += size
            newsum += new
            updsum += updated
            delsum += deleted
        
        #self.db.commit()
        log.debug("Directory %s finished" % host_dir)
        
        return (sizesum, newsum, updsum, delsum)
    
    #TODO: Find name for first function
    def start(self):
        #TODO: Docstring
        pass
    def run(self, host_dir="/"):
        #TODO: Docstring
        startTime = time.time()
        db_host = self.db.getHost(self.host.ip, self.host.hostname)
        db_dir = self.db.getService(db_host, self.host.type, self.host.username, self.host.password)
        
        (s, n, u, d) = self.walker(db_dir, host_dir)
        
        endTime = time.time()
        
        self.db.newStat(db_host, startTime, endTime, s, n, u, d)
        
        self.db.commit()
        
        log.info("Crawler statistics: New: %d, Updated: %d, Deleted: %d" % (n,u,d))
        
        return (s, n, u, d)