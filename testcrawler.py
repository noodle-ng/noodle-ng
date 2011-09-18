'''
Created on 12.09.2011

@author: moschlar
'''
import os, sys, time, logging, traceback
from noodle.lib.utils import urlSplit
from crawlerclass import CrawlerSMB, CrawlerFTP
from ConfigParser import SafeConfigParser

import transaction
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

import noodle.model as model

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

if __name__ == "__main__":
    
    engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    #model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    #model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    #model.metadata.create_all(engine)
    
    session = model.DBSession()
    
    path = u"smb://Gast:123Dabei@dns320/public/eBooks"
    url = urlSplit(path)
    t1 = time.time()
    try:
        crawlersmb = CrawlerSMB(session,url.hostname,(url.username,url.password))
        print crawlersmb.onewalk(url.path)
        (dirs,files) = crawlersmb.onewalk(url.path)
        print crawlersmb.listdir(url.path)
        print crawlersmb.isdir(url.path)
        print crawlersmb.isfile(url.path)
        print crawlersmb.stat(url.path+u"/OSP_wrobel_gentoo.pdf")
        (n,u,d) = crawlersmb.run(url.path)
        print "Crawler statistics: New: %d, Updated: %d, Deleted: %d" % (n,u,d)
        print "Session statistics: New: %d, Updated: %d, Deleted: %d" % (len(session.new), len(session.dirty), len(session.deleted))
        transaction.commit()
    except Exception, e:
        traceback.print_exc()
        transaction.doom()
    
    t2 = time.time()
    
    try:
        crawlerftp = CrawlerFTP(session,url.hostname,(url.username,url.password))
        print crawlerftp.onewalk(url.path)
        (dirs,files) = crawlerftp.onewalk(url.path)
        print crawlerftp.listdir(url.path)
        print crawlerftp.isdir(url.path)
        print crawlerftp.isfile(url.path)
        print crawlerftp.stat(url.path+u"/OSP_wrobel_gentoo.pdf")
        (n,u,d) = crawlerftp.run(url.path)
        print "Crawler statistics: New: %d, Updated: %d, Deleted: %d" % (n,u,d)
        print "Session statistics: New: %d, Updated: %d, Deleted: %d" % (len(session.new), len(session.dirty), len(session.deleted))
        transaction.commit()
    except Exception, e:
        traceback.print_exc()
        transaction.doom()
    
    t3 = time.time()
    
    print "SMB took %fs" % (t2-t1)
    print "FTP took %fs" % (t3-t2)
    