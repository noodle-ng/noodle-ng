'''
Created on 04.10.2011

@author: moschlar
'''

from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, BigInteger, DateTime, Float

import noodle.model
from noodle.model import BaseColumns, DeclarativeBase, metadata, DBSession

class Statistic(BaseColumns, DeclarativeBase):
    """Statistics base class"""
    __tablename__ = 'statistics'
    host_id = Column(Integer, ForeignKey('hosts.id'), nullable=False)
    type = Column(Unicode(20), nullable=False)
    __mapper_args__ = {'polymorphic_on': type}

class Ping(Statistic):
    """Holds information about one ping result"""
    #TODO: This should definitely hold a ping_type field that contains "smb" or "ftp"
    ping = Column(Float, nullable=True)
    __mapper_args__ = {'polymorphic_identity': u'ping'}
    
    def __init__(self, host=None, value=None):
        """Set ping results"""
        self.host = host
        self.value = value

class Crawl(Statistic):
    """Holds information about one crawl run for one host"""
    #TODO: Propably use HostCrawl und FullCrawl to distinguish between
    # the whole crawl process and the crawl process for one host
    # sqlite3 devdata.db 'SELECT statistics.crawl_time, hosts.name FROM statistics JOIN hosts on hosts.id == statistics.host_id WHERE statistics.type == "crawl" '
    crawl_time = Column(Float)
    new = Column(Integer)
    changed = Column(Integer)
    deleted = Column(Integer)
    sharesize = Column(BigInteger)
    #error = Column(Boolean)
    __mapper_args__ = {'polymorphic_identity': u'crawl'}
    
    def __init__(self, crawl_time, sharesize, new=None, changed=None, deleted=None):
        """Set crawl run statistics"""
        self.crawl_time = crawl_time
        self.sharesize = sharesize
        if new:
            self.new = new
        if changed:
            self.changed = changed
        if deleted:
            self.deleted = deleted

