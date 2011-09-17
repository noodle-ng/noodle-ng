#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import logging
import sys, os, commands
import re
import socket as sk
from datetime import datetime, timedelta
from multiprocessing import Pool
import ConfigParser

import smbc

import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

import noodle.model as model
from noodle.model.share import host, serviceSMB, folder, file

from noodle.lib.utils import pingSMB,ipToInt, intToIp
import noodle.lib.iptools as iptools


# Parsing configuration

config = ConfigParser.SafeConfigParser({'here': sys.path[0]})
try:
    config.read(os.path.join(sys.path[0], 'crawler.ini'))
except:
    sys.exit("Could not read crawler.ini")

# Get the database settings
sqlalchemy_url = config.get('main', 'sqlalchemy.url')
sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')
#Get the multiprocessing parameters
mp_processes = config.getint('main', 'processes')
# Get the debug setting
debug_mode = config.getboolean('main', 'debug')

# Parse main credentials as tuple
if config.has_option("main", "credentials"):
    main_credentials = eval(config.get("main", 'credentials'))
    if not isinstance(main_credentials, tuple):
        main_credentials = (main_credentials,)
else:
    main_credentials = ()

# Parse individual sections
sections = []
for sectionName in config.sections():
    if sectionName != "main":      # main is not allowed to have a range
        section = {}
        section["name"] = sectionName
        section["range"] = []
        try:
            range = config.get(sectionName, 'range')
        except:
            print "WARNING: no range found for %s" % sectionName
            continue
        for singlerange in range.split(","):
            singlerange = singlerange.strip()
            if len(singlerange.split("-")) > 1:
                # this is a ip range
                try:
                    range_start, range_stop = singlerange.split("-")
                except:
                    print "%s is not a valid range!" % singlerange
                    sys.exit(1)
                section["range"].append(iptools.IpRangeList( (range_start.strip(), range_stop.strip()) ))
            else:
                # its a single ip adress or CDIR
                section["range"].append(iptools.IpRangeList(singlerange))
        if config.has_option(sectionName, "credentials"):
            section_credentials = eval(config.get(sectionName, 'credentials'))
            if not isinstance(section_credentials, tuple):
                section_credentials = (section_credentials,)
        else:
            section_credentials = ()
        section["credentials"] = []
        for item in main_credentials:
            section["credentials"].append(item)
        for item in section_credentials:
            section["credentials"].append(item)
        sections.append(section)

# smbc_type constants
# 3 = Share
# 7 = Directory
# 8 = File
SMBC_SHARE = 3
SMBC_FOLDER = 7
SMBC_FILE = 8

def crawl(ip=False, credentials=[["anonymous", ""]]):
    
    def getDate(dateString):
        """ converts the string given by smbclient to a datetime object """
        date = datetime.strptime(dateString, "%a %b %d %H:%M:%S %Y")
        return date

    def getDnsEntry(ip):
        """ get the dns name for a given ip address """
        try:
            entry = sk.gethostbyaddr(ip)[0]
        except:
            entry = None
        return entry
    
    def splitFileName(s):
        name = ''
        ext = ''
        
        #reverse fileName s
        s = s[::-1]
        #if no dot in fileName s
        position = s.find('.')
        
        #if no dot in fileName s
        if position == -1 :
            name = s[::-1]
        #else split by dot
        else:
            ext = s[:position][::-1]
            name = s[position + 1:][::-1]
        return [name, ext]
    
    def getFolder(parent, path):
        qfolder = False
        path = path[1:].split('\\')
        folderName = path[0]
        for item in parent.children:
            if item.name == folderName:
                if isinstance(item, folder):
                    if len(path) > 1:
                        newPath = ""
                        for entry in path[1:]:
                            newPath += '\\' + entry
                        qfolder = getFolder(item, newPath)
                    else:
                        qfolder = item
                    break
        return qfolder
    
    
    def analyze(ip, credentials):
        """ Analyze the given host and return filesystem representation """
        
        def walker(c, dir, path):
            # dir must be smbc.Dir
            """ This function walks recursively through the directory you give him
            and returns folder()-Objects according to the model.
            
            For the sake of OOP this should be a class..."""
            #logging.info(path)
            
            theFolder = folder()
            #theFolder.name = unicode(path.split('/')[-2],'utf-8')
            theFolder.name = path.split('/')[-2]
            
            #logging.debug("%s in %s" %(dir,path))
            #logging.debug("walking through %s:" %path.split('/')[-2])
            #theFolder = ''
            
            #logging.debug(dir.getdents())
            
            
            # We get Folders and Files alphabetically sorted but totally mixed up here!
            # If we want to fix it, the question is: 
            # Fix it here (By looping two times through direntries)
            # or fix it in merge, when writing to the database ??
            direntries = dir.getdents()
            for entry in direntries:
                #logging.debug(entry)
                if entry.name.startswith('.'):
                    #Skipping . , .. and hidden files
                    continue
                elif entry.smbc_type == SMBC_FOLDER:
                    # a subdirectory
                    newPath = path + entry.name + '/'
                    try:
                        newDir = c.opendir(newPath)
                    except:
                        #logging.debug('Opening %s went wrong' % newPath)
                        continue
                    myFolder = walker(c, newDir, newPath)
                    theFolder.children.append(myFolder)
                    #theFolder += entry.name+'\n'+myFolder+'\n'
                    
                elif entry.smbc_type == SMBC_FILE:
                    # a file
                    myFile = file()
                    #myFile = ''
                    
                    name, extension = os.path.splitext(entry.name)
                    extension = extension[1:]
                    #myFile.name = unicode(name,'utf-8')
                    myFile.name = name
                    #myFile.extension = unicode(extension,'utf-8')
                    myFile.extension = extension
                    #myFile = name+'.'+extension
                    try:
                        f = c.open(path + entry.name)
                    except:
                        #logging.debug('Opening %s went wrong' % path+entry.name)
                        continue
                    fs = f.fstat()
                    myFile.size = fs[6]
                    try:
                        myFile.date = datetime.fromtimestamp(fs[8]) # mtime
                    except:
                        myFile.date = datetime.now()
                    #myFile += '\t%s\t%s'%(fs[6],fs[8])
                    theFolder.children.append(myFile)
                    #theFolder += '\t'+entry.name+'\n'
                else:
                    # a nothing
                    # "Uuuhhuuuuuuuuuu...."
                    continue
                
            return theFolder
        
        logging.info("analyzing " + str(ip) + " with pysmbc")
        #logging.info("creds: " + str(credentials))
        
        c = smbc.Context()
        
        services = []
        
        for (username, password) in credentials:
            shares = []
            if username == 'anonymous':
                uri = 'smb://%s/' % ip
            else:
                if debug_mode: logging.info('trying with %s:%s' % (username, password))
                uri = 'smb://%s:%s@%s/' % (username, password, ip)
            try:
                host = c.opendir(uri)
                #logging.debug(host)
                #shares = host.getdents()
                #logging.debug(shares)
                
                for share in host.getdents():
                    if debug_mode: logging.info(share.name)
                    if share.smbc_type == SMBC_SHARE:
                        path = uri +"%s/" % (share.name)
                        #logging.info(path)
                        try:
                            dir = c.opendir(path)
                            #logging.debug('In %s I have %s' % (share.name,dir.getdents()))
                            shares.append(share)
                        except:
                            # So this share is not accessible, who cares! Next one please!
                            continue
                
                if len(shares) > 0:
                    if debug_mode: logging.debug('I found something on %s:\n%s' % (ip, shares))
                    if debug_mode: logging.debug('I came there as %s:%s' % (username, password))
                    myService = serviceSMB()
                    myService.username = unicode(username)
                    myService.password = unicode(password)
                    
                    for share in shares:
                        path = uri +"%s/" % (share.name)
                        dir = c.opendir(path)
                        # Now we loop through all the content of share
                        # So we start the walker
                        theFolder = walker(c, dir, path)
                        #logging.debug(theFolder)
                        theFolder.name = unicode(share.name)
                        
                        myService.children.append(theFolder)
                        #myService += theFolder
                    services.append(myService)
            except:
                #logging.info('failed. trying again')
                continue
            
        # Trying to completely kill the smbContext
        c = None
        del c
        
        #logging.info(myService)
        return services
    
    def mergeTree(pdb, premote):
        """ merges the tree from the db (pdb) with the new crawled tree (premote) """
        
        # Propably it would be very improving to use merge() here!
        # http://www.sqlalchemy.org/docs/05/session.html#merging
        
        def generateList(tree):
            list = {}
            for child in tree.children:
                if hasattr(child, "extension"):
                    key = child.name + unicode(child.extension)
                    list[key] = child
                else:
                    key = child.name
                    list[key] = child
            return list
        
        dblist = generateList(pdb)
        remotelist = generateList(premote)
        
        #logging.info(dblist)
        
        for key in dblist:
            if key in remotelist:
                if hasattr(dblist[key], "children"):
                    mergeTree(dblist[key], remotelist[key])
                
                if (dblist[key].size != remotelist[key].size) or (dblist[key].date != remotelist[key].date):
                    logging.info("size or date of %s changed" % remotelist[key].name)
                    opfer = pdb.children[pdb.children.index(dblist[key])]
                    opfer.last_update = datetime.now()
                    opfer.date = remotelist[key].date
                    opfer.size = remotelist[key].size
                    logging.info(session.dirty)
                    logging.info(remotelist[key])
                    pdb.children[pdb.children.index(dblist[key])] = session.merge(opfer)
                del remotelist[key]
                
            else:
                logging.info(dblist[key])
                del pdb.children[ pdb.children.index(dblist[key]) ]
                session.delete(dblist[key])
                
        for key in remotelist:
            logging.info(remotelist[key])
            pdb.children.append(remotelist[key])
    
    if not ip:
        raise
    
    startTime = time.time()
    
    if getDnsEntry(ip):
        # check if the server is running a smb server  // timeout 3s
        if not pingSMB(ip, timeout=1):
            return
        
        session = model.DBSession()
        
        try:
            myhost = session.query(host).filter(host.ip_as_int == ipToInt(ip)).first()
        except:
            myhost = None
            
        if not myhost:
            myhost = host()
            myhost.ip = ip
            session.add(myhost)
        
        myhost.name = getDnsEntry(myhost.ip)
        myhost.last_crawled = datetime.now()
        #session.add(myhost)
        
        logging.debug(str(ip) + " analyzing Host")
        remoteServices = analyze(ip, credentials)
        if not remoteServices:
            # got no valid data
            return
        
        #print myhost.services
        #print remoteServices
        
        for remoteService in remoteServices:
            myserviceSMB = None
            for service in myhost.services:
                if isinstance(service, serviceSMB):
                    if (service.username == remoteService.username) \
                        and (service.password == remoteService.password):
                        myserviceSMB = service
            if not myserviceSMB:
                myserviceSMB = serviceSMB()
                myserviceSMB.host = myhost
                session.add(myserviceSMB)
            
            logging.debug(str(ip) + " merging Tree")
            mergeTree(myserviceSMB, remoteService)
            myserviceSMB.username = remoteService.username
            myserviceSMB.password = remoteService.password
        
        logging.debug(str(ip) + " done merging")
        myhost.crawl_time_in_s = int(time.time() - startTime)
        session.commit()
        session.close()
    return

def commitJob(ip, credentials):
    startTime = time.time()
    crawl(ip, credentials)
    endTime = time.time()
    return "crawled host " + ip + " in " + str(endTime - startTime) + " seconds"

def report(value):
    logging.info(value)

def setupProcess():
    """ setup the db connection for the worker """
    engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)

def debug(ip, credentials):
    """ setup the db connection for the worker """
    engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)
    crawl(ip, credentials)

if __name__ == '__main__':
    
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    
    if debug_mode:
        logging.info("running in debug mode")
        logging.info("beginn crawling")
        for section in sections:
            for range in section["range"]:
                for ip in range:
                    debug(ip, section["credentials"])
    else:
        logging.info("setting up worker pool")
        pool = Pool(processes=mp_processes, initializer=setupProcess)
        logging.info("beginn crawling")
        
        for section in sections:
            for range in section["range"]:
                for ip in range:
                    pool.apply_async(commitJob, [ip, section["credentials"]], callback=report)
        
        pool.close()
        pool.join()
    
    logging.info("deleting old entries")
    engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)
    
    session = model.DBSession()
    cutoff = datetime.now() - timedelta(days=24)
    for host in session.query(model.host).filter(model.host.last_crawled < cutoff).all():
        logging.info("deleting shares / host from host: " + str(host.name))
        session.query(model.share.share).filter(model.share.share.host_id == host.id).delete()
        session.delete(host)
    session.commit()
    
