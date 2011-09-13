#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This it the Noodle NG file crawler main module.

It is executable and will read it's configuration file and then
begin working based on the information it finds there.

"""

import sys, os, socket as sk
import logging
import multiprocessing
from ConfigParser import SafeConfigParser
from datetime import datetime

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit
from noodle.lib.iptools import IpRange, IpRangeList

import transaction
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

import noodle.model as model
from noodle.model.share import Host

fs = {'smb': False, 'ftp': False}
try:
    import crawler.fs_ftp as fs_ftp
    fs['ftp'] = True
except ImportError:
    pass
try:
    import crawler.fs_smb as fs_smb
    fs['smb'] = True
except ImportError:
    pass


# Some constant values
config_file = "crawler.ini"

# Parsing the overall configuration

config = SafeConfigParser({'here': sys.path[0]})
try:
    config.read(os.path.join(sys.path[0], config_file))
except:
    sys.exit("Could not read %s" % config_file)

debug = config.getboolean('main', 'debug')
if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)
processes = config.getint('main', 'processes')

sqlalchemy_url = config.get('main', 'sqlalchemy.url')
sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')

def setup_worker():
    """Sets up a worker process"""
    logging.debug("Setting up worker %s" % multiprocessing.current_process().name)
    engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    #model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    #model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    #model.metadata.create_all(engine)
    return

def crawl(host,type,credentials=None):
    """Starts the crawling process for one host"""
    logging.debug("Crawling host %s" % host)
    
    #u = urlsplit(url)
    
    hostname, ip = getHostAndAddr(host)
    if not hasService(ip, type):
        logging.debug("No %s share on %s" % (type, hostname))
        return
    
    session = model.DBSession()
    logging.debug(ipToInt(ip))
    try:
        # Find host or create a new one
        host = session.query(Host).filter(Host.ip == ipToInt(ip)).first() or Host(ip, unicode(hostname))
        logging.debug("On host %s" % intToIp(host.ip))
        session.merge(host)
        host.name = unicode(hostname)
        host.last_crawled = datetime.now()
        logging.debug("new: %s, dirty: %s" % (session.new, session.dirty))
        #session.flush()
        #logging.debug("new: %s, dirty: %s" % (session.new, session.dirty))
        #transaction.commit()
        
        logging.debug(host.services)
        for service in host.services:
            pass
        # find service with correct type
        # parent = host
        # for dir in url:
        #     dbdir = query(share).filter(parent = parent)
        #    merge dbdir, dir
        # def merge(dbdir,dir):
        #    for entry in dir:
        #        if entry in dbdir:
        #            we already have that,
        #            check for changes
        #        else:
        #            we dont have that, create it
        #        if entry is_instance(folder):
        #            recurse.
        logging.debug("new: %s, dirty: %s" % (session.new, session.dirty))
        transaction.commit()
    except Exception,e:
        logging.warning(e)
        transaction.doom()
    
    return

def main():
    """Runs the crawler"""
    global debug
    logging.info("Supported filesystems: %s" % fs)
    
    locations = []
    
    if len(sys.argv) > 1:
        debug = True
        # Parsing location configuration from argv
        for i in range(1, len(sys.argv)):
            url = urlSplit(sys.argv[i])
            location = {'name': "arg%d" % i, 'type': url.scheme, 
                        'hosts': [IpRange(sk.gethostbyname(url.hostname))], 
                        'credentials': [(url.username,url.password)]}
            locations.append(location)
    else:
        # Parsing location configuration from config file
        for name in [section for section in config.sections() if section != 'main']:
            
            location = {}
            location['name'] = name
            location['type'] = config.get(name, 'type')
            if not fs[location['type']]:
                logging.info("Type %s is not supported, skipping section %s" % (location['type'], name))
                continue
            hosts = []
            for element in config.get(name, 'hosts').split(','):
                element = element.strip()
                if element.find('-') != -1:
                    # IP range
                    start, stop = element.split('-', 1)
                    hosts.append((start.strip(), stop.strip()))
                else:
                    # CIDR range or single IP
                    hosts.append(element)
            location['hosts'] = IpRangeList(*hosts)
            location['credentials'] = []
            for cred in config.get(name, 'credentials').split(','):
                location['credentials'].append(tuple(cred.strip().split(':')))
            locations.append(location)
    
    logging.debug(locations)
    
    for location in locations:
        logging.debug("Crawling location %s" % location['name'])
        # Get minimum that we don't have to have more workers than jobs
        pool = multiprocessing.Pool(min(processes,len(location['hosts'])*len(location['credentials'])), setup_worker)
        
        for host in location['hosts']:
            pool.apply_async(crawl, (host, location['type'], location['credentials']))
        
        pool.close()
        pool.join()
    
    return

if __name__ == '__main__':
    main()
