#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This it the Noodle NG file crawler main module.

It is executable and will read it's configuration file and then
begin working based on the information it finds there.

"""
#TODO: Error handling
#TODO: Docstrings
#TODO: Logging (to file)

#TODO: What to do with unaccessible folders, or with unaccessible shares in root folder of smb
#TODO: Rename crawlerclass and remove crawler/fs* stuff
#TODO: Propably not use transaction in the crawler

#TODO: CleanUp imports
import sys, os
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

from crawlerclass import CrawlerSMB, CrawlerFTP
crawler_type = {"smb": CrawlerSMB, "ftp": CrawlerFTP}

log = logging.getLogger(__name__)

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
    processes = 0
else:
    logging.basicConfig(level=getattr(logging,config.get('main', 'logging.level')))
    processes = config.getint('main', 'processes')

sqlalchemy_url = config.get('main', 'sqlalchemy.url')
sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')

def parse_locations():
    #TODO: Docstrings
    #TODO: Error handling
    locations = []
    
    if len(sys.argv) > 1:
        # debug = True
        # Parsing location configuration from argv
        for i in range(1, len(sys.argv)):
            url = urlSplit(sys.argv[i])
            location = {'name': "arg%d" % i, 'type': url.scheme, 
                        'hosts': [url.hostname], 
                        'credentials': [(url.username, url.password)]}
            locations.append(location)
    else:
        # Parsing location configuration from config file
        for name in (section for section in config.sections() if section != 'main'):
            
            location = {}
            location['name'] = name
            location['type'] = config.get(name, 'type')
            
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
            if config.has_option(name, 'anonymous'):
                if config.getboolean(name, 'anonymous'):
                    location['credentials'].append((None, None))
            for cred in config.get(name, 'credentials').split(','):
                location['credentials'].append(tuple(cred.strip().split(':', 1)))
            locations.append(location)
    return locations

def setup_worker():
    """Sets up a worker process"""
    log.debug("Setting up worker %s" % multiprocessing.current_process().name)
    engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    model.init_model(engine)
    #model.metadata.create_all(engine)
    return

def crawl(host, type, credentials=None, initializer=None):
    """Starts the crawling process for one host"""
    if initializer:
        initializer()
    
    hostname, ip = getHostAndAddr(host)
    
    log.info("Crawling host %s (%s) for %s shares" % (hostname, ip, type))
    
    session = model.DBSession()
    
    #TODO: Error handling
    for (username, password) in credentials:
        try:
            crawler = crawler_type[type](session, host, unicode(username), unicode(password))
            crawler.run()
        except Exception, e:
            log.warn(e)
            raise
    
    return

def main():
    """Runs the crawler"""
    global debug
    
    locations = parse_locations()
    
    log.info("Locations to crawl: %s" % locations)
    
    if processes == 0:
        for location in locations:
            log.info("Crawling location %s" % location['name'])
            for host in location['hosts']:
                crawl(host, location['type'], location['credentials'], setup_worker)
    else:
        # Get minimum that we don't have to have more workers than jobs
        #TODO: Error handling - Find out what can go wrong with a worker pool
        pool = multiprocessing.Pool(processes, setup_worker)
        for location in locations:
            log.info("Crawling location %s" % location['name'])
            for host in location['hosts']:
                pool.apply_async(crawl, (host, location['type'], location['credentials']))
        pool.close()
        pool.join()
    
    return

if __name__ == '__main__':
    main()
