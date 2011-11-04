'''
Created on 21.09.2011

@author: moschlar
'''
#TODO: Docstring

import logging

from sqlalchemy.orm import sessionmaker, scoped_session, exc
from sqlalchemy import create_engine, event

from noodle.lib.utils import ipToInt, intToIp, hasService, getHostAndAddr, urlSplit, urlUnsplit
import noodle.model as model
from noodle.model import Host, Folder, File, Service, ServiceSMB, ServiceFTP, Crawl, before_commit

log = logging.getLogger("DatabaseSession")

service_type = {"smb": ServiceSMB, "ftp": ServiceFTP}
#TODO: Docstring

class DatabaseSession():
    """DatabaseSession performs all database operations"""
    
    def __init__(self, url, echo=False):
        """Initialize DatabaseSession
        
        Especially important is to register the commit and flush hooks
        to get correct timestamp and host values
        """
    #    engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
    #    model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
    #    model.DBSession = scoped_session(model.maker)
    #    model.init_model(engine)
    #    model.metadata.create_all(engine)
        engine = create_engine(url, echo=echo)
        model.maker = sessionmaker(bind=engine, autoflush=True, autocommit=False, extension=None)
        model.DBSession = scoped_session(model.maker)
        self.session = model.DBSession
        
        # Register custom hooks
        event.listen(self.session, "before_commit", before_commit)
        event.listen(self.session, "before_flush", before_commit)

    #TODO: Move as classmethod to model
    def getHost(self, ip, hostname):
        """Get the host for the given ip
        
        If the host is already in the database, return it
        if not, create a new Host object, add it to the session and return it
        """
        try:
            host = self.session.query(Host).filter(Host.ip == ipToInt(ip)).one()
        except exc.NoResultFound:
            host = Host(ipToInt(ip), unicode(hostname))
            self.session.add(host)
        except exc.MultipleResultsFound:
            log.error("Database inconsistency detected")
            # Because host.ip is defined UNIQUE in the model,
            # this case should really never ever happen
            #for host in self.session.query(Host).filter(Host.ip == ipToInt(ip)).all():
            #    self.session.delete(host)
            raise
        else:
            # Update hostname
            if host.name != unicode(hostname):
                host.name = unicode(hostname)
        return host
    
    #TODO: Move as classmethod to model
    def getService(self, host, type, username, password):
        """Get a service for a given host, type and credentials
        
        If a service with the given parameters does already exist in the
        database, return it
        it not, create a new Service object, add it to the session 
        and return it
        """
        try:
            service = self.session.query(service_type[type]).filter(Service.host==host).filter(Service.username == username).filter(Service.password == password).one()
        except exc.NoResultFound:
            service = service_type[type](username, password)
            host.services.append(service)
            self.session.add(service)
        except exc.MultipleResultsFound:
            log.error("Database inconsistency detected")
            raise
        return service
    
    #TODO: Move as classmethod to model
    def newStat(self, host, startTime, endTime, s, n, u, d):
        """Make a new Stat object for a crawl"""
        crawl = Crawl(endTime-startTime,s,n,u,d)
        host.statistics.append(crawl)
        return crawl
    
    def commit(self):
        """Commit changes in the current session to the database"""
        self.session.commit()
    
    def debug(self):
        """Print out session object instance state information for
        debugging purposes"""
        log.debug("New: %s, Dirty: %s, Deleted: %s" % (self.session.new, self.session.dirty, self.session.deleted))
