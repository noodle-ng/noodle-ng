# -*- coding: utf-8 -*-
"""Noodle share model"""

from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, BigInteger, DateTime#, Float, Numeric

import noodle.model
from noodle.model import DeclarativeBase, metadata, DBSession

#from noodle.lib.utils import ipToInt, intToIp 

videoExt = [u"avi", u"mkv", u"mp4", u"mpv", u"mov", u"mpg", u"divx", u"vdr"]
audioExt = [u"mp3", u"aac", u"ogg", u"m4a", u"wav"]
mediaExt = videoExt + audioExt

def makePretty(value):
    ''' convert bit values in human readable form '''
    steps = [ (1024, u"KiB"), (1048576, u"MiB"), (1073741824, u"GiB"), (1099511627776, u"TiB") ]
    for step in steps:
        m = step[0]
        suffix = step[1]
        try:
            cs = value / m
        except:
            return u""
        if cs < 10:
            return u"%3.1f" % (cs) + ' ' + suffix
        if cs < 1024:
            return unicode(int(cs)) + ' ' + suffix
    return u"very big"

class Share(DeclarativeBase):
    __tablename__ = 'shares'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('shares.id'))
    host_id = Column(Integer, ForeignKey('hosts.id'))
    # the filename without extension if the item has one
    name = Column(Unicode(256))
    # the creation date of the item which the hosts provides
    date = Column(DateTime)
    # the date the crawler first indexed the item
    first_seen = Column(DateTime, nullable=False)
    # date the last time the item was updated by the crawler (i.e. size changed)
    last_update = Column(DateTime, nullable=False)
    #meta = relation("meta", uselist=False, backref="share")
    type = Column(Unicode(20), nullable=False)
    __mapper_args__ = {'polymorphic_on': type}
    
    def __init__(self, first_seen=datetime.now(), last_update=datetime.now()):
        ''' set the first_seen and last_update fields'''
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


class Folderish(Share):
    children = relationship(Share, cascade="all", backref=backref('parent', remote_side="Share.id"))
    #children = relation("share", cascade="all, delete-orphan", backref=backref('parent', remote_side="share.id"))
    __mapper_args__ = {'polymorphic_identity': u'folderish'}
    
    def __init__(self,**kwargs):
        Share.__init__(self, **kwargs)
    
    def getMediaType(self):
        return "folder"
    
    mediaType = property(getMediaType)

class Content(Share):
    size = Column(BigInteger)
    #host = relation("host")
    __mapper_args__ = {'polymorphic_identity': u'content'}
    
    def __init__(self, name, **kwargs):
        Share.__init__(self, **kwargs)
        self.name = name

class Folder(Folderish, Content):
    __mapper_args__ = {'polymorphic_identity': u'folder'}
    
    def __init__(self, name, **kwargs):
        Content.__init__(self, name)

class File(Content):
    # file extension, if there is one
    extension = Column(Unicode(256))
    # can hold a hash value to find same files, could be nice 
    # to introduce load balancing to proxyDownloader
    hash = Column(Unicode(256))
    __mapper_args__ = {'polymorphic_identity': u'file'}
    
    def __init__(self, name, ext, **kwargs):
        Content.__init__(self, name)
        self.extension = ext
    
    def update(self,date=None,size=None):
        if date:
            self.date = date
        if size:
            self.size = size
        self.last_update = datetime.now()
        return
        
    def getPath(self):
        return self.parent.getPath()
    
    def getShowPath(self):
        path = unicode(self.parent.getShowPath()) + "/" + self.name
        if self.extension != None:
            return unicode(path + "." + self.extension)
        else:
            return unicode(path)

class Service(Folderish):
    username = Column(Unicode(256))
    password = Column(Unicode(256))
    __mapper_args__ = {'polymorphic_identity': u'service'}
    
    def __init__(self, username=None, password=None, **kwargs):
        Folderish.__init__(self, **kwargs)
        if username:
            self.username = username
            if password:
                self.password = password
    
    def getService(self):
        return self
    
    def getPath(self):
        return unicode(self.host.ip)
    
    def getShowPath(self):
        return u""

class ServiceSMB(Service):
    __mapper_args__ = {'polymorphic_identity': u'serviceSMB'}

class ServiceFTP(Service):
    __mapper_args__ = {'polymorphic_identity': u'serviceFTP'}

###############################################################################

class Statistic(DeclarativeBase):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    type = Column(Unicode(20), nullable=False)
    __mapper_args__ = {'polymorphic_on': type}

class Ping(Statistic):
    value = Column(Float, nullable=True)
    __mapper_args__ = {'polymorphic_identity': u'ping'}
    
    def __init__(self, host=None, value=None, date=datetime.now()):
        self.host = host
        self.value = value
        self.date = date

###############################################################################

class Host(DeclarativeBase):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    ip = Column(BigInteger, nullable=False)
    name = Column(Unicode(256))
    first_seen = Column(DateTime, nullable=False)
    last_update = Column(DateTime, nullable=False)
    crawl_time = Column(Integer)
    sharesize = Column(BigInteger)
    services = relationship(Service, backref="host")
    statistics = relationship(Statistic, backref="host")
    
    def __init__(self, ip, name=None, first_seen=datetime.now(), last_update=datetime.now()):
        self.ip = ip
        if name:
            self.name = name
        self.first_seen = first_seen
        self.last_update = last_update
    
    #@property
    def getPrettyShareSize(self):
        return makePretty(self.sharesize)
    
    prettyShareSize = property(getPrettyShareSize)
