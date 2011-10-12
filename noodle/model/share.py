# -*- coding: utf-8 -*-
"""Noodle share model"""
#TODO: Docstrings
#TODO: Unicode awareness
#TODO: Reconcile all functions here to new model structure
#TODO: Probably use isFolder or isFile functions instead of getMediaType
#TODO: Put setting of last_update into generic model handling to avoid having to set it everytime
#TODO: Convention in CakePHP framework is : created, modified fields are automatically set and updated
#      -> first_seen = created, last_update = modified
#TODO: classmethods

import logging
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relationship, backref
from sqlalchemy import Table, ForeignKey, Column, func
from sqlalchemy.types import Integer, Unicode, BigInteger, DateTime, Float

import noodle.model
from noodle.model import BaseColumns, DeclarativeBase, metadata, DBSession
from stats import Statistic
#from noodle.lib.utils import ipToInt, intToIp 

videoExt = [u"avi", u"mkv", u"mp4", u"mpv", u"mov", u"mpg", u"divx", u"vdr"]
audioExt = [u"mp3", u"aac", u"ogg", u"m4a", u"wav"]
mediaExt = videoExt + audioExt

def getShareSum():
    #TODO: Docstring
    try:
        sharesum = DBSession.query(func.sum(Host.sharesize)).one()[0]
    except Exception as e:
        logging.warn(e)
        sharesum = 0
    return makePretty(sharesum)

def makePretty(value):
    ''' convert bit values in human readable form '''
    #TODO: Does this belong here?
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

class Share(BaseColumns, DeclarativeBase):
    #TODO: Docstrings
    __tablename__ = 'shares'
    parent_id = Column(Integer, ForeignKey('shares.id'))
    host_id = Column(Integer, ForeignKey('hosts.id'))
    # the filename without extension if the item has one
    name = Column(Unicode(256))
    # the creation date of the item which the hosts provides
    date = Column(DateTime)
    #meta = relation("meta", uselist=False, backref="share")
    type = Column(Unicode(20), nullable=False)
    
    __mapper_args__ = {'polymorphic_on': type}
    
    def __init__(self):
        #TODO: Docstrings
        pass
    
    def __before_commit__(self, session=False, status=False):
        #TODO: Docstrings
        #TODO: This isn't called anymore
        if session and status == "new":
            if self.host == None:
                self.host = self.getHost()
    
    def getHost(self):
        #TODO: Docstrings
        if hasattr(self, "host"):
            if self.host != None:
                return self.host
        if hasattr(self, "parent"):
            if self.parent != None:
                return self.parent.getHost()
        return None
    
    def getService(self):
        #TODO: Docstrings
        return self.parent.getService()
    
    def getPath(self):
        #TODO: Docstrings
        return unicode(self.parent.getPath()) + "/" + self.name
    
    def getShowPath(self):
        #TODO: Docstrings
        return unicode(self.parent.getShowPath()) + "/" + self.name
    
    def getPrettySize(self):
        #TODO: Docstrings
        return makePretty(self.size)
    
    def getNameWithExt(self):
        #TODO: Docstrings
        if hasattr(self, "extension"):
            if self.extension != None:
                return self.name + u"." + self.extension
        return self.name
    
    def getMediaType(self):
        #TODO: Docstrings
        if hasattr(self, "extension"):
            if self.extension in videoExt:
                return "video"
            elif self.extension in audioExt:
                return "audio"
        return "file"
    
    def getCredentials(self):
        #TODO: Docstrings
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
    #TODO: Docstrings
    children = relationship(Share, cascade="all", backref=backref('parent', remote_side="Share.id"))
    #TODO: Why not delete-orphan
    #children = relation("share", cascade="all, delete-orphan", backref=backref('parent', remote_side="share.id"))
    __mapper_args__ = {'polymorphic_identity': u'folderish'}
    
    def __init__(self,**kwargs):
        #TODO: Docstrings
        Share.__init__(self, **kwargs)
    
    @property
    def childDict(self):
        #TODO: Docstrings
        folders = {}
        files = {}
        for child in self.children:
            if isinstance(child, Folder):
                folders[child.name] = child
            elif isinstance(child, File):
                if child.extension:
                    files[child.name + child.extension] = child
                else:
                    files[child.name] = child
            else:
                continue
        return (folders, files)
    
    def getMediaType(self):
        #TODO: Docstrings
        return "folder"
    
    mediaType = property(getMediaType)

class Content(Share):
    #TODO: Docstrings
    size = Column(BigInteger)
    #host = relation("host")
    __mapper_args__ = {'polymorphic_identity': u'content'}
    
    def __init__(self, name, **kwargs):
        #TODO: Docstrings
        Share.__init__(self, **kwargs)
        self.name = name

class Folder(Folderish, Content):
    #TODO: Docstrings
    __mapper_args__ = {'polymorphic_identity': u'folder'}
    
    def __init__(self, name, **kwargs):
        #TODO: Docstrings
        Content.__init__(self, name)

class File(Content):
    #TODO: Docstrings
    # file extension, if there is one
    extension = Column(Unicode(256))
    # can hold a hash value to find same files, could be nice 
    # to introduce load balancing to proxyDownloader
    hash = Column(Unicode(256))
    __mapper_args__ = {'polymorphic_identity': u'file'}
    
    def __init__(self, name, ext, **kwargs):
        #TODO: Docstrings
        Content.__init__(self, name)
        self.extension = ext
    
    def update(self,date=None,size=None):
        #TODO: Docstrings
        if date:
            self.date = date
        if size:
            self.size = size
        self.last_update = datetime.now()
        return
        
    def getPath(self):
        #TODO: Docstrings
        return self.parent.getPath()
    
    def getShowPath(self):
        #TODO: Docstrings
        path = unicode(self.parent.getShowPath()) + "/" + self.name
        if self.extension != None:
            return unicode(path + self.extension)
        else:
            return unicode(path)

class Service(Folderish):
    #TODO: Docstrings
    username = Column(Unicode(256))
    password = Column(Unicode(256))
    __mapper_args__ = {'polymorphic_identity': u'service'}
    
    def __init__(self, username=None, password=None, **kwargs):
        #TODO: Docstrings
        Folderish.__init__(self, **kwargs)
        if username:
            self.username = username
            if password:
                self.password = password
    
    def getService(self):
        #TODO: Docstrings
        return self
    
    def getPath(self):
        #TODO: Docstrings
        return unicode(self.host.ip)
    
    def getShowPath(self):
        #TODO: Docstrings
        return u""

class ServiceSMB(Service):
    #TODO: Docstrings
    short_type = "smb"
    __mapper_args__ = {'polymorphic_identity': u'serviceSMB'}

class ServiceFTP(Service):
    #TODO: Docstrings
    short_type = "ftp"
    __mapper_args__ = {'polymorphic_identity': u'serviceFTP'}

###############################################################################

class Host(BaseColumns, DeclarativeBase):
    #TODO: Docstrings
    __tablename__ = 'hosts'
    ip = Column(BigInteger, nullable=False, unique=True)
    name = Column(Unicode(256))
    #TODO: Deprecate crawl_time here, instead move it to statistics
    crawl_time = Column(Float)
    sharesize = Column(BigInteger)
    services = relationship(Service, backref="host")
    statistics = relationship(Statistic, backref="host")
    
    def __init__(self, ip, name=None):
        #TODO: Docstrings
        self.ip = ip
        if name:
            self.name = name
    
    #TODO:
    @classmethod
    def by_ip(cls, ip, hostname):
        #TODO: Docstrings
        pass
    
    #@property
    def getPrettyShareSize(self):
        #TODO: Docstrings
        return makePretty(self.sharesize)
    
    prettyShareSize = property(getPrettyShareSize)
