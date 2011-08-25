# -*- coding: utf-8 -*-
"""Noodle share model"""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, BigInteger, DateTime

from noodle.model import DeclarativeBase, metadata, DBSession

class Host(DeclarativeBase):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    ip = Column(BigInteger, nullable=False)
    name = Column(Unicode(256), nullable=False)
    last_crawled = Column(DateTime)
    crawl_time_in_s = Column(Integer)
    sharesize = Column(BigInteger)
    services = relation(Share, primaryjoin=and_(id == share.host_id, share.parent_id == None), backref="host")
    statistics = relation(Statistic, primaryjoin=id == statistic.host_id, backref="host")

class Share(DeclarativeBase):
    __tablename__ = 'shares'
    id = Column(Integer, primary_key=True)
    type = Column(Unicode(20), nullable=False)
    parent_id = Column(Integer, ForeignKey('shares.id'))
    host_id = Column(Integer, ForeignKey('hosts.id'), nullable=False)
    name = Column(Unicode(256))
    date = Column(DateTime)
    first_seen = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)
    #meta = relation("meta", uselist=False, backref="share")
    __mapper_args__ = {'polymorphic_on': type}
    
    def __init__(self, first_seen=datetime.now(), last_update=datetime.now()):
        ''' set the first_seen and last_update fields for convenience sake '''
        self.first_seen = first_seen
        self.last_update = last_update
    
    def __before_commit__(self, session=False, status=False):
        if session and status == "new":
            if self.host == None:
                self.host = self.getHost()
    
    def getHost(self):
        if hasattr(self, "host"):
            if self.host != None:
                return self.host
        if hasattr(self, "parent"):
            if self.parent != None:
                return self.parent.getHost()
        return None
    
    def getService(self):
        return self.parent.getService()
    
    def getPath(self):
        return unicode(self.parent.getPath()) + "/" + self.name
    
    def getShowPath(self):
        return unicode(self.parent.getShowPath()) + "/" + self.name
    
    def getPrettySize(self):
        return makePretty(self.size)
    
    def getNameWithExt(self):
        if hasattr(self, "extension"):
            if self.extension != None:
                return self.name + u"." + self.extension
        return self.name
    
    def getMediaType(self):
        if hasattr(self, "extension"):
            if self.extension in videoExt:
                return "video"
            elif self.extension in audioExt:
                return "audio"
        return "file"
    
    def getCredentials(self):
        service = self.getService()
        creds = {}
        if service.username:
            creds["username"] = service.username
            creds["password"] = service.password
        else:
            creds["username"] = "anonymous"
            creds["password"] = ""
        return creds
    
    prettySize = property(getPrettySize)
    nameWithExt = property(getNameWithExt)
    mediaType = property(getMediaType)
