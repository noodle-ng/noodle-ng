'''
Created on 05.09.2011

@author: moschlar
'''

import logging, posixpath
from datetime import datetime

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit

import transaction
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

import noodle.model as model
from noodle.model.share import Host, Folder, File

class Crawler():
    
    def __init__(self, type, session, hostname, ip, credentials=None):
        self.type = type
        self.session = session
        self.hostname = hostname
        self.ip = ip
        self.credentials = credentials
    
    def path_split(self, path):
        return posixpath.split(path)
    
    def path_join(self,a,*p):
        return posixpath.join(a,*p)
    
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
    
    def run(self, host_dir="/"):
        #print self.session.query(Host).filter(Host.ip == ipToInt(self.ip)).all()
        host = self.session.query(Host).filter(Host.ip == ipToInt(self.ip)).first() or Host(self.ip, unicode(self.hostname))
        self.session.add(host)
        host.name = unicode(self.hostname)
        host.last_crawled = datetime.now()
        print host.services
        database_dir = host.getService(self.type, self.credentials)
        self.session.add(database_dir)
        print database_dir
        print database_dir.children
        return self.walker(database_dir, host_dir)
    
    def walker(self, database_dir, host_dir):
        
        logging.debug("Directory %s started" % host_dir)
        
        host_folders, host_files = self.onewalk(host_dir)
        db_folders, db_files = self.dblist(database_dir)
        
        logging.debug("host_list: %s %s" % (str(host_folders), str(host_files)))
        logging.debug("database_list: %s %s" % (str(db_folders), str(db_files)))
        
        newFiles = set(f for f in host_files) - set(f for f in db_files)
        newFolders = set(f for f in host_folders) - set(f for f in db_folders)
        updateFiles = set(f for f in host_files) & set(f for f in db_files)
        updateFolders = set(f for f in host_folders) & set(f for f in db_folders)
        delFiles = set(f for f in db_files) - set(f for f in host_files)
        delFolders = set(f for f in db_folders) - set(f for f in db_folders)
        
        for newFile in newFiles:
            logging.debug("New: %s" % newFile)
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
            logging.debug("Update: %s" % updateFile)
            #name, ext = self.path_splitext(updateFile)
            stat = self.stat(self.path_join(host_dir, updateFile))
            file = db_files[updateFile]
            if file.size != stat[6] or file.date != datetime.fromtimestamp(stat[8]):
                logging.debug("   Changed: %s" % updateFile)
                file.size = stat[6]
                file.date = datetime.fromtimestamp(stat[8])
                file.last_update = datetime.now()
        
        for delFile in delFiles:
            logging.debug("Delete: %s" % delFile)
            del database_dir.children[database_dir.children.index(delFile)]
        
        for newFolder in newFolders:
            logging.debug("New: %s" % newFolder)
            folder = Folder(newFolder)
            folder.last_update = datetime.now()
            database_dir.children.append(folder)
            db_folders[newFolder] = folder
        
        for updateFolder in updateFolders:
            logging.debug("Update: %s" % updateFolder)
            pass
            folder = db_folders[updateFolder]
            folder.last_update = datetime.now()
        
        for delFolder in delFolders:
            logging.debug("Delete: %s" % delFolder)
            del database_dir.children[database_dir.children.index(delFolder)]
        
        newsum=0
        delsum=0
        
        for folder in db_folders.itervalues():
            new,deleted = self.walker(folder,self.path_join(host_dir, folder.name))
            newsum+=new
            delsum+=deleted
        
        logging.debug("Directory %s finished" % host_dir)
        #return (len(newFiles),len(newFolders),len(updateFiles), len(updateFolders), len(delFiles), len(delFolders))
        return (len(newFiles)+len(newFolders)+newsum,len(delFiles)+len(delFolders)+delsum)
        
        for file in host_files:
            hf = set(f for f in host_files)
            df = set(f for f in db_files)
            logging.info("new: %s, update: %s, delete: %s" % (hf-df, hf&df, df-hf))
            stat = self.stat(self.path_join(host_dir, file))
            if file in db_files:
                # File already crawled
                logging.debug("File already crawled: %s" % file)
                if db_files[file].size != stat[6] or db_files[file].date != datetime.fromtimestamp(stat[8]):
                    # Stats have changed
                    logging.debug("File changed: %s" % file)
                    db_files[file].size = stat[6]
                    db_files[file].date = datetime.fromtimestamp(stat[8])
                    db_files[file].last_update = datetime.now()
            else:
                # New file
                logging.debug("New file: %s" % file)
                myFile = File()
                name, extension = self.path_splitext(file)
                myFile.name = name
                myFile.extension = extension
                myFile.size = stat[6]
                myFile.date = datetime.fromtimestamp(stat[8])
                myFile.last_update = datetime.now()
                database_dir.children.append(myFile)
        
        for folder in host_folders:
            if folder in db_folders:
                # Folder already crawled
                logging.debug("Folder already crawled: %s" % folder)
                self.walker(db_folders[folder], self.path_join(host_dir, folder))
            else:
                # New Folder
                logging.debug("New folder: %s" % folder)
                myFolder = Folder()
                myFolder.name = folder
                myFolder.last_update = datetime.now()
                database_dir.children.append(myFolder)
                self.walker(myFolder, self.path_join(host_dir, folder))
            
        logging.debug("Directory %s finished" % host_dir)
    