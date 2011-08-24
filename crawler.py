#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This it the Noodle NG file crawler main module.

It is executable and will read it's configuration file and then
begin working based on the information it finds there.

"""

import sys, os, socket as sk
import logging
from multiprocessing import Pool
from ConfigParser import SafeConfigParser
from urlparse import urlparse

from noodle.lib.iptools import IpRange,IpRangeList

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
processes = config.getint('main', 'processes')

sqlalchemy_url = config.get('main', 'sqlalchemy.url')
sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')

def setup_worker(type):
    """Sets up a worker process"""
    logging.debug("setting up worker for %s" % type)
    
    return

def crawl(host):
    """Starts the crawling process for one host"""
    logging.debug("Crawling host %s" % host)
    
    return

def main():
    """Runs the crawler"""
    
    locations = []
    
    if len(sys.argv) > 1:
        debug = True
        # Parsing location configuration from argv
        for i in range(1, len(sys.argv)):
            url = urlparse(sys.argv[i])
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
        pool = Pool(min(processes,len(location['hosts'])), setup_worker, (location['type'],))
        pool.map_async(crawl, location['hosts'])
        pool.close()
        pool.join()
    
    return

if __name__ == '__main__':
    main()
