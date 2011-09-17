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
    u = urlSplit(path)
    t1 = time.time()
    try:
        crawlersmb = CrawlerSMB(session,u.hostname,(u.username,u.password))
        print crawlersmb.onewalk(u.path)
        (dirs,files) = crawlersmb.onewalk(u.path)
        print crawlersmb.listdir(u.path)
        print crawlersmb.isdir(u.path)
        print crawlersmb.isfile(u.path)
        print crawlersmb.stat(u.path+u"/OSP_wrobel_gentoo.pdf")
        crawlersmb.run()
        transaction.commit()
    except Exception, e:
        print "Narf: %s" % e
        traceback.print_exc()
        transaction.doom()
    
    t2 = time.time()
    
    try:
        raise
        crawlerftp = CrawlerFTP(session,u.hostname,(u.username,u.password))
        print crawlerftp.onewalk(u.path)
        (dirs,files) = crawlerftp.onewalk(u.path)
        print crawlerftp.listdir(u.path)
        print crawlerftp.isdir(u.path)
        print crawlerftp.isfile(u.path)
        print crawlerftp.stat(u.path+u"/OSP_wrobel_gentoo.pdf")
        crawlerftp.run()
        transaction.commit()
    except Exception, e:
        print "Narf: %s" % e
        transaction.doom()
    
    t3 = time.time()
    
    print "SMB took %f" % (t2-t1)
    print "FTP took %f" % (t3-t2)
    