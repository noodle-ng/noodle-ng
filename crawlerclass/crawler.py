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
                    files[child.name+"."+child.extension] = child
                else:
                    files[child.name] = child
            else:
                continue
            
        return (folders, files)
    
    def run(self):
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
        host_dir = "/public/eBooks"
        self.walker(database_dir, host_dir)
    
    def walker(self, database_dir, host_dir):
        
        host_list = self.onewalk(host_dir)
        database_list = self.dblist(database_dir)
        
        print "host_list: %s" % str(host_list)
        print "database_list: %s" % str(database_list)
        
        for file in host_list[1]:
            stat = self.stat(self.path_join(host_dir,file))
            if file in database_list[1]:
                # File already crawled
                print file + " already crawled"
                if database_list[1][file].size != stat[6] or database_list[file].date != datetime.fromtimestamp(stat[8]):
                    # Stats have changed
                    print file + "changed"
                    database_list[1][file].size = stat[6]
                    database_list[1][file].date = datetime.fromtimestamp(stat[8])
                    database_list[1][file].last_update = datetime.now()
            else:
                # New file
                print file + "new"
                myFile = File()
                name, extension = self.path_splitext(file)
                myFile.name = name
                myFile.extension = extension
                myFile.size = stat[6]
                myFile.date = datetime.fromtimestamp(stat[8])
                myFile.last_update = datetime.now()
                database_dir.children.append(myFile)
        
        for folder in host_list[0]:
            if folder in database_list[0]:
                # Folder already crawled
                print folder + "already crawled"
                self.walker(database_list[0][folder], self.path_join(host_dir, folder))
            else:
                # New Folder
                logging.debug("New folder: %s" % folder)
                myFolder = Folder()
                myFolder.name = folder
                myFolder.last_update = datetime.now()
                database_dir.children.append(myFolder)
                self.walker(myFolder, self.path_join(host_dir, folder))
            
        print "finished"
    