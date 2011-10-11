#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this script checks the validity of the database. 
# ===========================================
# || IT WILL DELETE ANY NON VALID ENTRIES! ||
# ===========================================


import sys, os
import logging
import ConfigParser
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import select, delete
import noodle.model as model
from noodle.model.share import share, host


servicePrincipals = ["serviceSMB", "serviceFTP"]

validHosts    = [] #contains the IDs of valid hosts
invalidHosts  = []
validShares   = []
invalidShares = []


def checkItem(id, conn):
    def checkHost(host_id):
        if host_id in validHosts:
            return True
        if host_id in invalidHosts:
            return False
        item = conn.execute( select([host.id], host.id==host_id) ).fetchone()
        if not item:
            logging.debug("host with id: %i does not exist" % id)
            invalidHosts.append(host_id)
            return False
        else:
            # host is valid
            validHosts.append(host_id)
            return True
            
    item = conn.execute( select([share.id, share.parent_id, share.host_id, share.type], share.id==id) ).fetchone()
    if not item:
        logging.debug("share with id: %i does not exist" % id)
        invalidShares.append(id)
        return False
    id          = int( item[0] )
    parent_id   = item[1]
    if parent_id:
        parent_id = int(parent_id)
    host_id     = int( item[2] )
    type        = unicode( item[3] )
    logging.debug("id: %i parent_id: %s host_id: %i type: %s" % (id, str(parent_id), host_id, type))
    
    if id in invalidShares:
        return False
    
    if host_id in invalidHosts:
        invalidShares.append(id)
        return False
    
    if not checkHost(host_id):
        invalidShares.append(id)
        return False
    
    if type in servicePrincipals:
        # this is a root element of the share tree. Checking Host.
        if parent_id:
            # there should be no parent ID
            invalidShares.append(id)
            return False

        validShares.append(id)
        return True
    
    # check if the "path" is walkable
    if not checkItem(parent_id, conn):
        invalidShares.append(id)
        return False
    
    return True
    
        

if __name__ == '__main__':
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
    conn = engine.connect()
    checkConn = engine.connect()
    checkTrans = checkConn.begin()
    
    for item in conn.execute( select([share.id],) ):
        logging.debug("checking id: %i" % item[0])
        checkItem(item[0], checkConn)
    
    logging.info("valid Shares: %i  invalid Shares: %i  valid Hosts: %i  invalid Hosts: %i" % (len(validShares), len(invalidShares), len(validHosts), len(invalidHosts)) )
    logging.info("deleting invalid db entries")
    for id in invalidShares:
        logging.debug("deleting share id: %i" % id)
        checkConn.execute( delete(share.__table__, share.id==id) )
    checkTrans.commit()
    logging.info("committing ...")
    