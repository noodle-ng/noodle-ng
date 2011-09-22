'''
Created on 12.09.2011

@author: moschlar
'''
import os, sys, time, logging, traceback
from noodle.lib.utils import urlSplit
#from crawlerclass import CrawlerSMB, CrawlerFTP
from ConfigParser import SafeConfigParser
from crawl.smb import SMBHost
from crawl.database import DatabaseSession
from crawl import host_type
from crawl.crawler import Crawler

config_file = "crawler.ini"

# Parsing the overall configuration

config = SafeConfigParser({'here': sys.path[0]})
try:
    config.read(os.path.join(sys.path[0], config_file))
except:
    sys.exit("Could not read %s" % config_file)

logging.basicConfig(level=logging.DEBUG)

sqlalchemy_url = config.get('main', 'sqlalchemy.url')
sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')

path = u"smb://Gast:123Dabei@dns320/"
url = urlSplit(path)

def main():
    host = host_type[url.scheme](url.hostname, url.username, url.password)
    db = DatabaseSession(sqlalchemy_url, sqlalchemy_echo)
    
    crawler = Crawler(db, host)
    crawler.run(url.path)


if __name__ == "__main__":
    main()
