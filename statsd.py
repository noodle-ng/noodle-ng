#!/usr/bin/env python
# -*- coding: iso-8859-1 -*-

import sys, os
import logging
import ConfigParser
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import select
import noodle.model as model


def calculateShare(host_id):
    session = model.DBSession()
    conn = engine.connect()
    host = session.query(model.host).filter(model.host.id == host_id).one()
    
    sharesize = 0
    
    for item in conn.execute( select([model.share.file.size], model.share.file.host_id==host.id) ):
        if item[0] > 0:
            sharesize += item[0]
    
    host.sharesize = sharesize
    session.commit()
    return


if __name__ == '__main__':
    # parsing the config
    config = ConfigParser.SafeConfigParser({'here': sys.path[0]})
    try:
        config.read(os.path.join(sys.path[0], 'crawler.ini'))
    except:
        sys.exit("Could not read crawler.ini")
    
    sqlalchemy_url = config.get('main', 'sqlalchemy.url')
    sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')
    debug_mode = config.getboolean('main', 'debug')
    
    FORMAT = "%(asctime)-15s %(message)s"
    if debug_mode:
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    else:
        logging.basicConfig(level=logging.INFO, format=FORMAT)
    
    engine = sqlalchemy.create_engine(sqlalchemy_url)
    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    model.DBSession = scoped_session(model.maker)
    model.init_model(engine)
    model.metadata.create_all(engine)
    session = model.DBSession()
    
    for host in session.query(model.host).all():
        logging.info("begin host %s - %s" % (host.ip, host.name))
        calculateShare(host.id)
