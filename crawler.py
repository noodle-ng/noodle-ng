#!/usr/bin/env python
# -*- coding: utf-8 -*-
#BETA BETA BETA BETA BETA BETA BETA BETA BETA BETA
"""
This it the Noodle NG file crawler main module.

It is executable and will read it's configuration file and then
begin working based on the information it finds there.

"""
#TODO: Error handling
#TODO: Docstrings
#TODO: Logging (to file)
#TODO: Rename type that's used everywhere

#TODO: What to do with unaccessible folders, or with unaccessible shares in root folder of smb
#TODO: Rename crawlerclass and remove crawler/fs* stuff
#TODO: Propably not use transaction in the crawler

#TODO: CleanUp imports
import sys, os, logging, multiprocessing
from ConfigParser import SafeConfigParser

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit
from noodle.lib.iptools import IpRange, IpRangeList

from crawling import host_type, Crawler, DatabaseSession, SMBHost

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
    # Ignore logging level and multiprocessing
    logging.basicConfig(level=logging.DEBUG)
    processes = 0
else:
    logging.basicConfig(level=getattr(logging,config.get('main', 'logging.level')))
    processes = config.getint('main', 'processes')

sqlalchemy_url = config.get('main', 'sqlalchemy.url')
sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')

#BETA BETA BETA BETA BETA BETA BETA BETA BETA BETA

def parse_locations():
    """Parse the location either from argv (if given) or from
    the configuration file"""
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
            try:
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
            except Exception as e:
                log.warn(e)
    return locations

def setup_worker():
    """Sets up a worker process"""
    #log.debug("Setting up worker %s" % multiprocessing.current_process().name)
    #engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    #model.init_model(engine)
    #model.metadata.create_all(engine)
    return

def crawl(host, type, credentials=None, initializer=None):
    """Starts the crawling process for one host"""
    if initializer:
        # We only use this if no multiprocessing is used
        initializer()
    
    hostname, ip = getHostAndAddr(host)
    
    log.info("Crawling host %s (%s) for %s shares" % (hostname, ip, type))
    
    #session = model.DBSession()
    db = DatabaseSession(sqlalchemy_url, sqlalchemy_echo)
    #TODO: Error handling
    for (username, password) in credentials:
        try:
            #crawler = crawler_type[type](session, host, unicode(username), unicode(password))
            #crawler.run()
            crawlhost = host_type[type](host, username, password)
            crawler = Crawler(db, crawlhost)
            crawler.run()
        except Exception, e:
            log.warn(e)
            raise
    
    return

def main():
    """Runs the crawler"""
    global debug
    
    print "GAMMA GAMMA GAMMA GAMMA GAMMA GAMMA GAMMA!"
    
    locations = parse_locations()
    
    log.info("Locations to crawl: %s" % locations)
    
    if processes == 0:
        # No multiprocessing
        for location in locations:
            log.info("Crawling location %s" % location['name'])
            for host in location['hosts']:
                crawl(host, location['type'], location['credentials'], setup_worker)
    else:
        #TODO: Error handling - Find out what can go wrong with a worker pool
        #TODO: Handle stopping of child processes if parent process receives KeyboardInterrupt or similar
        pool = multiprocessing.Pool(min(processes,sum(len(location['hosts']) for location in locations)), setup_worker)
        for location in locations:
            log.info("Crawling location %s" % location['name'])
            for host in location['hosts']:
                pool.apply_async(crawl, (host, location['type'], location['credentials']))
        pool.close()
        pool.join()
    
    return

if __name__ == '__main__':
    main()
