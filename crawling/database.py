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
from noodle.model import Host, Folder, File, Service, ServiceSMB, ServiceFTP, Crawl, update_timestamps

log = logging.getLogger("DatabaseSession")

service_type = {"smb": ServiceSMB, "ftp": ServiceFTP}
#TODO: Docstring

class DatabaseSession():
    
    def __init__(self, url, echo=False):
        #TODO: Docstring
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
        
        event.listen(self.session, "before_commit", update_timestamps)
        event.listen(self.session, "before_flush", update_timestamps)

    
    def getHost(self, ip, hostname):
        #TODO: Docstring
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
            if host.name != unicode(hostname):
                host.name = unicode(hostname)
        return host
    
    def getService(self, host, type, username, password):
        #TODO: Docstring
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
    
    def newStat(self, host, startTime, endTime, s, n, u, d):
        #TODO: Docstring
        crawl = Crawl(endTime-startTime,s,n,u,d)
        host.statistics.append(crawl)
        return crawl
    
    def commit(self):
        self.session.commit()
    
    def debug(self):
        log.debug("New: %s, Dirty: %s, Deleted: %s" % (self.session.new, self.session.dirty, self.session.deleted))
