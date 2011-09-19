'''
Created on 05.09.2011

@author: moschlar
'''

import logging, posixpath, time
from datetime import datetime

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit

import transaction
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

import noodle.model as model
from noodle.model.share import Host, Folder, File, ServiceSMB, ServiceFTP
service_type = {"smb": ServiceSMB, "ftp": ServiceFTP}

log = logging.getLogger(__name__)

class Crawler():
    
    def __init__(self, type, session, hostname, ip, username=None, password=None):
        self.type = type
        self.session = session
        self.hostname = hostname
        self.ip = ip
        self.username = username
        self.password = password
    
    def path_split(self, path):
        return posixpath.split(path)
    
    def path_join(self, a, *p):
        return posixpath.join(a, *p)
    
    def path_splitext(self, file):
        return posixpath.splitext(file)
    
    def dblist(self, database_dir):
        folders = {}
        files = {}
        for child in database_dir.children:
            if isinstance(child, Folder):
                folders[child.name] = child
            elif isinstance(child, File):
                if child.extension:
                    files[child.name + child.extension] = child
                else:
                    files[child.name] = child
            else:
                continue
        return (folders, files)
    
    def walker(self, database_dir, host_dir):
        
        log.debug("Started crawling %s" % host_dir)
        
        # Variables for tracking statistics
        newsum = updsum = delsum = 0
        
        # Get lists for host and database
        host_folders, host_files = self.onewalk(host_dir)
        db_folders, db_files = self.dblist(database_dir)
        
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
            stat = self.stat(self.path_join(host_dir, newFile))
            file = File(name, ext)
            file.name = name
            file.extension = ext
            file.size = stat[6]
            file.date = datetime.fromtimestamp(stat[8])
            file.last_update = datetime.now()
            database_dir.children.append(file)
        
        for updateFile in updateFiles:
            log.debug("Update: %s" % updateFile)
            #name, ext = self.path_splitext(updateFile) # won't change, because it wouldn't be the same file then
            stat = self.stat(self.path_join(host_dir, updateFile))
            file = db_files[updateFile]
            if file.size != stat[6] or file.date != datetime.fromtimestamp(stat[8]):
                log.debug("   Changed: %s" % updateFile)
                updsum += 1
                file.size = stat[6]
                file.date = datetime.fromtimestamp(stat[8])
                file.last_update = datetime.now()
        
        for delFile in delFiles:
            log.debug("Delete: %s" % delFile)
            delsum += 1
            del database_dir.children[database_dir.children.index(delFile)]
        
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
            # Not sure what to do here, since we mostly can't get stats from a directory
            folder = db_folders[updateFolder]
            folder.last_update = datetime.now()
        
        for delFolder in delFolders:
            log.debug("Delete: %s" % delFolder)
            delsum += 1
            del database_dir.children[database_dir.children.index(delFolder)]
        
        # Perform recursive walking and sum up the stats
        for folder in db_folders.itervalues():
            new, updated, deleted = self.walker(folder,self.path_join(host_dir, folder.name))
            newsum += new
            updsum += updated
            delsum += deleted
        
        log.debug("Directory %s finished" % host_dir)
        
        return (newsum, updsum, delsum)
    
    def run(self, host_dir=u"/"):
        startTime = time.time()
        host = self.session.query(Host).filter(Host.ip == ipToInt(self.ip)).first() or Host(ipToInt(self.ip), unicode(self.hostname))
        self.session.add(host)
        host.name = unicode(self.hostname)
        
        database_dir = None
        # Try to get service of current type and current credentials
        for service in host.services:
            if isinstance(service, service_type[self.type]):
                if (service.username, service.password) == (self.username, self.password):
                    database_dir = service
        # If None exists, create one
        if not database_dir:
            database_dir = service_type[self.type](self.username, self.password)
            host.services.append(database_dir)
        
        self.session.add(database_dir)
        
        result = self.walker(database_dir, host_dir)
        
        endTime = time.time()
        host.crawl_time = int(round(endTime - startTime))
        log.debug("Crawl time: %d" % host.crawl_time)
        log.debug("Crawler statistics: New: %d, Updated: %d, Deleted: %d" % result)
        log.debug("Session statistics: New: %d, Updated: %d, Deleted: %d" % (len(self.session.new), len(self.session.dirty), len(self.session.deleted)))
        
        transaction.commit()
        
        return result