#!/usr/bin/env python
# -*- coding: utf-8 -*-

from multiprocessing import Pool
import time
import logging
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
import noodle.model as model

# getting database url from production.ini
try:
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    #config.read('development.ini')
    config.read('production.ini')
    url = config.get('app:main','sqlalchemy.url',raw=True)
    if not url: raise
except:
    url = 'sqlite:///%(here)s/somedb.db'

credentials = [ ["Gast", "123Dabei"], ["anonymous"] ]

def crawl(ip=False):
    
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
        name=''
        ext=''
        
        #reverse fileName s
        s=s[::-1]
        #if no dot in fileName s
        position=s.find('.')
        
        #if no dot in fileName s
        if position == -1 :
            name=s[::-1]
        #else split by dot
        else:
            ext=s[:position][::-1]
            name=s[position+1:][::-1]
        return [name,ext]
    
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
    
    def analyze(ip):
        """ analyze a given host and return a representation of the filesystem """
        
        logging.debug(str(ip) + " running smbclient" )
        
        # get list of shares
        list = []
        for credential in credentials:
            if len(list) > 0:
                break
            
            if credential[0] != "anonymous":
                username = credential[0]
                password = credential[1]
                s = commands.getstatusoutput('smbclient -gL ' + ip + ' ' + "-U " + username + "%" + password )[1].split('\n')
            else:
                username = "anonymous"
                password = ""
                s = commands.getstatusoutput('smbclient -gL ' + ip + ' -N')[1].split('\n')
            
            for i in s:
                if 'Disk|' in i:
                    if username != "anonymous":
                        list.append(["-U " + username + "%" + password, i.split('|')[1].replace("'", "'\\''")])
                    else:
                        list.append(["-N", i.split('|')[1].replace("'", "'\\''")])
        # if we got no shares due to invalid incredentials break
        if len(list) == 0:
            return False
        
        logging.debug(str(ip) + " analyzing smbclient output" )
        myService = serviceSMB()
        myService.username = username
        myService.password = password
        for login, share in list:
            myFolder = folder()
            myFolder.name = share
            myService.children.append(myFolder)
            s = commands.getstatusoutput(r"smbclient  '\\%s\%s'  %s -c 'recurse ; ls *'  2>/dev/null " % (ip, share, login))
            s = s[1].decode('utf-8')
            cfolder = myFolder
            for line in s.splitlines():
                #print line.encode('ascii', 'replace')
                reFolder = re.findall(r"^((\\[^\\^\s]+(\s{1,2}[^\\^\s]+)*)+)", line)
                if len(reFolder) > 0:
                    myFolder = getFolder(myService, u"\\" + share + reFolder[0][0])
                if not myFolder:
                    # because we can not parse the output of smbclient right it can happen, that we do not have the right directory structure
                    # this is only a dirty hack to at least get all parsable data and only to throw away the data we can't parse
                    logging.warning("skipping due to folder not Found")
                    continue
                reData = re.findall(r"^  (([^\s]+\s{1,2})+)\s+(\w{0,3})\s+(\d+)\s+(\w+\s+\w+\s+\d{1,2}\s+\d{1,2}:\d{1,2}:\d{1,2}\s\d{4})$", line)
                if len(reData) > 0:
                    name, trash, mode, size, date = reData[0]
                    name = name[0:-2] # very dirty hack. Need to change the re
                    date = getDate(date)
                    # Modes:
                    # H hidden
                    # R read only
                    # A Archive
                    if "D" in mode:
                        # this entry is a Folder
                        if name == ".": # myFolder
                            myFolder.date = date
                        elif name == "..":
                            pass
                        else:
                            newFolder = folder()
                            newFolder.name = name
                            newFolder.date = date
                            myFolder.children.append(newFolder)
                    else:
                        # ok, it is a file
                        newFile = file()
                        name, extension = splitFileName(name)
                        newFile.name = name
                        newFile.extension = extension
                        newFile.date = date
                        newFile.size = size
                        myFolder.children.append(newFile)
        return myService
    
    def mergeTree(pdb, premote):
        """ merges the tree from the db (pdb) with the new crawled tree (premote) """
        
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
        
        for key in dblist:
            if key in remotelist:
                
                if hasattr(dblist[key], "children"):
                    mergeTree(dblist[key], remotelist[key])
                del remotelist[key]
                
            else:
                del pdb.children[ pdb.children.index(dblist[key]) ]
                session.delete(dblist[key])
                
        for key in remotelist:
            pdb.children.append(remotelist[key])
        
    if not ip:
        raise
    
    import commands
    import re
    from datetime import datetime
    import time
    import socket as sk
    import noodle.model as model
    from noodle.model.share import ipToInt, intToIp, host, serviceSMB, folder, file
    
    startTime = time.time()
    
    if getDnsEntry(ip):
        # check if the server is running a smb server  // timeout 1s
        sd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        sd.settimeout(1)
        try:
            sd.connect((ip, 445))
            sd.close()
        except:
            return
        
        session = model.DBSession()
        
        try:
            myhost = session.query(host).filter( host.ip_as_int==ipToInt(ip) ).first()
        except:
            myhost = host()
            myhost.ip = ip
            
        if not myhost:
            myhost = host()
            myhost.ip = ip
        
        myhost.name = getDnsEntry(myhost.ip)
        myhost.last_crawled = datetime.now()
        session.add(myhost)
        
        logging.debug(str(ip) + " analyzing Host")
        remoteService = analyze(ip)
        if not remoteService:
            # got no valid data
            return
        
        hasServiceSMB = False
        for service in myhost.services:
            if isinstance(service, serviceSMB):
                hasServiceSMB = True
                myserviceSMB = service
        if not hasServiceSMB:
            myserviceSMB = serviceSMB()
            myserviceSMB.host = myhost
            session.add(myserviceSMB)
        
        logging.debug( str(ip) + " merging Tree" )
        mergeTree(myserviceSMB, remoteService)
        myserviceSMB.username = remoteService.username
        myserviceSMB.password = remoteService.password
        
        logging.debug( str(ip) + " done merging" )
        myhost.crawl_time_in_s = int( time.time() - startTime )
        session.commit()
        session.close()
    return


def commitJob(ip):
    startTime = time.time()
    crawl(ip)
    endTime = time.time()
    return "crawled host " + ip + " in " + str(endTime - startTime) + " seconds"

def report(value):
    logging.info(value)

def setupProcess():
    """ setup the db connection for the worker """
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker, scoped_session
    import noodle.model as model
    
    verbose = False
    engine = sqlalchemy.create_engine(url, echo=verbose)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)



def debug(ip):
    """ setup the db connection for the worker """
    import sqlalchemy
    from sqlalchemy.orm import sessionmaker, scoped_session
    import noodle.model as model
    
    logging.debug(str(ip) + " analyzing Host")
    
    verbose = False
    engine = sqlalchemy.create_engine(url, echo=verbose)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)
    crawl(ip)


if __name__ == '__main__':
    
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    
    logging.info("generating hostlist")
    hostlist = []
    for i in range(48, 80):
        for j in range(1, 255):
            hostlist.append("134.93." + str(i) + "." + str(j) )
    
    logging.info("setting up worker pool")
    pool = Pool(processes=10, initializer=setupProcess)
    logging.info("beginn crawling")
    hostlist = ["134.93.51.1",]
    for host in hostlist:
        #pool.apply_async(commitJob, [host], callback=report)
        debug(host)
    pool.close()
    pool.join()
    
    logging.info("deleting old entries")
    engine = sqlalchemy.create_engine(url)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)
    
    session = model.DBSession()
    cutoff = datetime.now() - timedelta(days=24)
    for host in session.query(model.host).filter(model.host.last_crawled < cutoff).all():
        logging.info( "deleting shares / host from host: " + str(host.name) )
        session.query(model.share.share).filter(model.share.share.host_id == host.id).delete()
        session.delete(host)
    session.commit()
    
