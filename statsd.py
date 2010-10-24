#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-
""" Der Stats Daemon berechnet, ja, wie der Name schon sagt Statistiken ;) """

from multiprocessing import Pool, Process
import time
import logging
from datetime import datetime, timedelta
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import select
import noodle.model as model

try:
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    #config.read('development.ini')
    config.read('production.ini')
    url = config.get('app:main','sqlalchemy.url',raw=True)
    if not url: raise
except:
    url = 'sqlite:///%(here)s/somedb.db'

def calculateShare(host_id):
    session = model.DBSession()
    conn = engine.connect()
    host = session.query(model.host).filter(model.host.id == host_id).one()
    logging.info("begin host " + str(host.name))
    
    sharesize = 0
    
    for item in conn.execute( select([model.share.file.size], model.share.file.host_id==host.id) ):
        if item[0] > 0:
            sharesize += item[0]
    
    host.sharesize = sharesize
    session.commit()
    return ("host " + str(host.name) + " done")

def debug(host_id):
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
    calculateShare(host_id)
    
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


if __name__ == '__main__':
    
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    
    logging.info("setting up worker pool")
    pool = Pool(processes=10, initializer=setupProcess)
    logging.info("calculating share stats per host")
    
    engine = sqlalchemy.create_engine(url)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)
    
    session = model.DBSession()
    
    for host in session.query(model.host).all():
        #pool.apply_async(calculateShare, [host.id], callback=report)
        debug(host.id)
    pool.close()
    pool.join()
    