'''
Created on 21.09.2011

@author: moschlar
'''
#TODO: Docstring

import logging, time
from datetime import datetime

from noodle.model.share import Folder, File

log = logging.getLogger("Crawler")

class Crawler():
    """Crawler main class
    
    Performs the crawling steps that merge the tree from
    the host and the database and everything inbetween
    """
    
    def __init__(self, databasesession, host, extension=None):
        #TODO: Docstring
        
        self.db = databasesession
        self.session = self.db.session
        self.host = host
        self.extension = extension
    
    def walker(self, database_dir, host_dir):
        """Recursive walking function"""
        
        log.debug("Started crawling %s" % host_dir)
        
        # Variables for tracking statistics
        sizesum = newsum = updsum = delsum = 0
        
        # Get lists for host and database
        host_folders, host_files = self.host.onewalk(host_dir)
        db_folders, db_files = database_dir.childDict
        
        log.debug("host_list: %s %s" % (str(host_folders), str(host_files)))
        log.debug("database_list: %s %s" % (str(db_folders), str(db_files)))
        
        # We use sets here because we can perform union, intersection and complement operations on them
        newFiles = set(f for f in host_files) - set(f for f in db_files)
        newFolders = set(f for f in host_folders) - set(f for f in db_folders)
        
        updateFiles = set(f for f in host_files) & set(f for f in db_files)
        updateFolders = set(f for f in host_folders) & set(f for f in db_folders)
        
        delFiles = set(f for f in db_files) - set(f for f in host_files)
        delFolders = set(f for f in db_folders) - set(f for f in host_folders)
        
        log.debug("newFiles: %s" % newFiles)
        for newFile in newFiles:
            log.debug("New file: %s" % newFile)
            newsum += 1
            name, ext = self.host.path_splitext(newFile)
            stat = self.host.stat(self.host.path_join(host_dir, newFile))
            file = File(name, ext)
            #file.name = name
            #file.extension = ext
            file.size = stat.size
            sizesum += file.size
            file.date = datetime.fromtimestamp(stat.mtime)
            #file.last_update = datetime.now()
            database_dir.children.append(file)
            assert file in self.session
            assert file in database_dir.children
        
        log.debug("newFolders: %s" % newFolders)
        for newFolder in newFolders:
            log.debug("New folder: %s" % newFolder)
            newsum += 1
            stat = self.host.stat(self.host.path_join(host_dir, newFolder))
            folder = Folder(newFolder)
            folder.size = stat.size
            folder.date = datetime.fromtimestamp(stat.mtime)
            #folder.last_update = datetime.now()
            database_dir.children.append(folder)
            db_folders[newFolder] = folder
            assert folder in self.session
            assert folder in database_dir.children
        
        log.debug("updateFiles: %s" % updateFiles)
        for updateFile in updateFiles:
            #log.debug("Update: %s" % updateFile)
            #name, ext = self.host.path_splitext(updateFile) # won't change, because it wouldn't be the same file then
            stat = self.host.stat(self.host.path_join(host_dir, updateFile))
            file = db_files[updateFile]
            #log.debug(file in self.session)
            assert file in self.session
            assert file in database_dir.children
            if file.size != stat.size or file.date != datetime.fromtimestamp(stat.mtime):
                log.debug("Changed file: %s" % updateFile)
                updsum += 1
                file.size = stat.size
                file.date = datetime.fromtimestamp(stat.mtime)
                #file.last_update = datetime.now()
            else:
                log.debug("Not changed file: %s" % updateFile)
            sizesum += file.size
        
        log.debug("updateFolders: %s" % (updateFolders))
        for updateFolder in updateFolders:
            #log.debug("Update: %s" % updateFolder)
            stat = self.host.stat(self.host.path_join(host_dir, updateFolder))
            folder = db_folders[updateFolder]
            #log.debug(folder in self.session)
            assert folder in self.session
            assert folder in database_dir.children
            if folder.size != stat.size or folder.date != datetime.fromtimestamp(stat.mtime):
                log.debug("Changed folder: %s" % updateFolder)
                updsum += 1
                log.debug(folder.size)
                log.debug(stat.size)
                log.debug(folder.date)
                log.debug(datetime.fromtimestamp(stat.mtime))
                folder.size = stat.size
                log.debug(type(folder.size))
                # For whatever reason, folder.size is never ever saved to the database
                log.debug(folder in self.session.dirty)
                folder.date = datetime.fromtimestamp(stat.mtime)
                #file.last_update = datetime.now()
                #log.debug("Changed: %d %d %d %d" % (folder.size, stat.size, folder.date, datetime.fromtimestamp(stat.mtime)))
                #self.session.add(folder)
            else:
                log.debug("Not changed folder: %s" % updateFile)
        
        log.debug("delFiles: %s" % (delFiles))
        for delFile in delFiles:
            log.debug("Deleted file: %s" % delFile)
            delsum += 1
            file = db_files[delFile]
            assert file in self.session
            assert file in database_dir.children
            try:
                # Sometimes there were errors about an item not being in the list
                #del database_dir.children[database_dir.children.index(delFile)]
                database_dir.children.remove(file)
            except Exception as e:
                log.warning("Could not delete %s from database: %s" % (delFile, e))
            #del db_files[delFile]
            self.session.delete(db_files[delFile])
            assert file not in database_dir.children
            assert file not in self.session
        
        log.debug("delFolders: %s" % (delFolders))
        for delFolder in delFolders:
            log.debug("Deleted folder: %s" % delFolder)
            delsum += 1
            folder = db_folders[delFolder]
            assert folder in self.session
            assert folder in database_dir.children
            try:
                # Sometimes there were errors about an item not being in the list
                #del database_dir.children[database_dir.children.index(db_folders[delFolder])]
                database_dir.children.remove(folder)
            except Exception as e:
                log.warning("Could not delete %s from database: %s" % (delFolder, e))
            del db_folders[delFolder]
            self.session.delete(folder)
            log.debug("%s %s %s" % (self.session.new,self.session.dirty,self.session.deleted))
            assert folder not in database_dir.children
            assert folder not in self.session
        
        #self.session.flush()
        
        # Perform recursive walking and sum up the stats
        for folder in db_folders.itervalues():
            size, new, updated, deleted = self.walker(folder, self.host.path_join(host_dir, folder.name))
            sizesum += size
            newsum += new
            updsum += updated
            delsum += deleted
        
        #self.db.commit()
        log.debug("Directory %s finished" % host_dir)
        
        return (sizesum, newsum, updsum, delsum)
    
    def getFolder(self, service, path):
        """Get the database top folder if crawling was started
        with a given path."""
        dir = service
        assert dir in self.session
        for p in (p for p in self.host.path_fullsplit(path) if p):
            if p in dir.childDict[0]:
                log.debug("already there")
                assert dir in self.session
                dir = dir.childDict[0][p]
            else:
                log.debug("not already there")
                folder = Folder(p)
                dir.children.append(folder)
                dir = folder
                assert dir in self.session
        assert dir in self.session
        return dir
        
    #TODO: Find name for first function
    def start(self):
        #TODO: Docstring
        self.run()
    def run(self, host_dir=""):
        """Get top folder or service from database and from host
        and start the recursive walking process"""
        startTime = time.time()
        db_host = self.db.getHost(self.host.ip, self.host.hostname)
        assert db_host in self.session
        db_serv = self.db.getService(db_host, self.host.type, self.host.username, self.host.password)
        assert db_serv in self.session
        db_dir = self.getFolder(db_serv, host_dir)
        assert db_dir in self.session
        #self.session.commit()
        
        (s, n, u, d) = self.walker(db_dir, host_dir)
        
        endTime = time.time()
        
        self.db.newStat(db_host, startTime, endTime, s, n, u, d)
        # 1 new and 1 dirty objects in session are from the stat above
        log.debug("Session statistics: New: %d, Updated: %d, Deleted: %d" % (len(self.session.new), len(self.session.dirty), len(self.session.deleted)))
        
        self.session.commit()
        
        log.info("Crawler statistics: New: %d, Updated: %d, Deleted: %d, Sharesize: %ld, Crawling time: %f" % (n,u,d,s,endTime-startTime))
        
        return (s, n, u, d)
    
