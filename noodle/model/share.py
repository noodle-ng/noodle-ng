# -*- coding: utf-8 -*-
from datetime import datetime

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref, object_session
from sqlalchemy.orm.interfaces import MapperExtension, SessionExtension
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, DateTime, Float, Binary, Numeric

from noodle.model import DeclarativeBase, metadata, DBSession

# dirty switch to 3rd party iptools (renaming will be soon)
from noodle.lib.iptools import ip2long as ipToInt, long2ip as intToIp 

videoExt = [u"avi", u"mkv", u"mp4", u"mpv", u"mov", u"mpg", u"divx", u"vdr"]
audioExt = [u"mp3", u"aac", u"ogg", u"m4a", u"wav"]

mediaExt = videoExt[:]
mediaExt.extend(audioExt)

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
            return unicode( int(cs) ) + ' ' + suffix
    return u"very big"

class meta(DeclarativeBase):
    __tablename__ = 'meta'
    id = Column(Integer, primary_key=True)
    share_id = Column(Integer, ForeignKey('shares.id'), nullable=False)
    atoms = relation("metaAtom", backref="meta")
    title   = Column(Unicode(128))
    artist  = Column(Unicode(128))
    album   = Column(Unicode(128))
    date    = Column(DateTime)
    comment = Column(Unicode(1024))
    genre   = Column(Unicode(128))
    length  = Column(Float())

class metaAtom(DeclarativeBase):
    __tablename__ = 'meta_atoms'
    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('meta.id'), nullable=False)
    type = Column(Unicode(20), nullable=False)
    __mapper_args__ = {'polymorphic_on': type}
    
class metaVideo(metaAtom):
    __tablename__ = 'meta_video'
    __mapper_args__ = {'polymorphic_identity': 'video'}
    id = Column(Integer, ForeignKey('meta_atoms.id'), primary_key=True)
    xres = Column(Integer)
    yres = Column(Integer)
    bitrate = Column(Integer)
    codec = Column(Unicode(20))
    fps = Column(Float())

class metaAudio(metaAtom):
    __tablename__ = 'meta_audio'
    __mapper_args__ = {'polymorphic_identity': 'audio'}
    id = Column(Integer, ForeignKey('meta_atoms.id'), primary_key=True)
    bitrate = Column(Integer)
    rate = Column(Integer)
    language = Column(Unicode(20))
    channels = Column(Integer)
    codec = Column(Unicode(20))

class metaPicture(metaAtom):
    __tablename__ = 'meta_picture'
    __mapper_args__ = {'polymorphic_identity': 'picture'}
    id = Column(Integer, ForeignKey('meta_atoms.id'), primary_key=True)
    xres = Column(Integer)
    yres = Column(Integer)
    codec = Column(Unicode(20))
    data = Column(Binary())

class share(DeclarativeBase):
    __tablename__ = 'shares'
    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey('shares.id'))
    host_id = Column(Integer, ForeignKey('hosts.id'), nullable=False)
    name = Column(Unicode(256))                     # the filename without extension if the item has one
    type = Column(Unicode(20), nullable=False)
    date = Column(DateTime)                         # the creation date of the item which the hosts provides
    first_seen = Column(DateTime, nullable=False)                   # the date the crawler first indexed the item
    last_update = Column(DateTime, nullable=False)                  # date the last time the item was updated by the crawler (i.e. size changed)
    meta = relation("meta", uselist=False, backref="share")
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
    
    def getService(self):
        return self.parent.getService()
    
    def getPath(self):
        return unicode(self.parent.getPath()) + "/" + self.name
    
    def getShowPath(self):
        return unicode(self.parent.getShowPath()) + "/" + self.name
        
    def getPrettySize(self):
        return makePretty(self.size)
    
    prettySize = property(getPrettySize)
    
    def getNameWithExt(self):
        if hasattr(self, "extension"):
            if self.extension != None:
                return self.name + u"." + self.extension
        return self.name
    
    nameWithExt = property(getNameWithExt)
    
    def getMediaType(self):
        if hasattr(self, "extension"):
            if self.extension in videoExt:
                return "video"
            elif self.extension in audioExt:
                return "audio"
        return "file"
    
    mediaType = property(getMediaType)
    
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


class folderish(share):
    __mapper_args__ = {'polymorphic_identity': 'folderish'}
    children = relation("share", cascade="all", backref=backref('parent', remote_side="share.id"))
    #children = relation("share", cascade="all, delete-orphan", backref=backref('parent', remote_side="share.id"))
    def getMediaType(self):
        return "folder"
    mediaType = property(getMediaType)
    
class content(share):
    __mapper_args__ = {'polymorphic_identity': 'content'}
    size = Column(Numeric(precision=32, scale=0, asdecimal=True))
    #host = relation("host")
    
class folder(folderish, content):
    __mapper_args__ = {'polymorphic_identity': 'folder'}

class file(content):
    __mapper_args__ = {'polymorphic_identity': 'file'}
    extension = Column(Unicode(256))    # file extension, if there is one
    hash = Column(Unicode(256))         # can hold a hash value to find same files
    
    def getPath(self):
        return self.parent.getPath()
    
    def getShowPath(self):
        path = unicode(self.parent.getShowPath()) + "/" + self.name
        if self.extension != None:
            return unicode( path + "." + self.extension )
        else:
            return unicode(path)

 
class service(folderish):
    __mapper_args__ = {'polymorphic_identity': 'service'}
    username = Column(Unicode(256))
    password = Column(Unicode(256))
    
    def getService(self):
        return self
    
    def getPath(self):
        return unicode(self.host.ip)
    
    def getShowPath(self):
        return u""

class serviceSMB(service):
    __mapper_args__ = {'polymorphic_identity': 'serviceSMB'}
    
class serviceFTP(service):
    __mapper_args__ = {'polymorphic_identity': 'serviceFTP'}

class statistic(DeclarativeBase):
    __tablename__ = 'statistic'
    id = Column(Integer, primary_key=True)
    host_id = Column(Integer, ForeignKey('hosts.id'), nullable=False)
    type = Column(Unicode(20), nullable=False)
    date = Column(DateTime, nullable=False)
    __mapper_args__ = {'polymorphic_on': type}
    
class ping(statistic):
    __mapper_args__ = {'polymorphic_identity': 'ping'}
    value = Column(Float, nullable=True)
    
    def __init__(self, host=None, value=None, date=datetime.now()):
        self.host = host
        self.value = value
        self.date = date
        
      
        
class host(DeclarativeBase):
    __tablename__ = 'hosts'
    id = Column(Integer, primary_key=True)
    
    # asdecimal=True may be dangerous when using iptools 
    ip_as_int = Column("ip", Numeric(precision=10, scale=0, asdecimal=True), nullable=False)
    name = Column(Unicode(256))
    services = relation(share, primaryjoin = and_(id == share.host_id, share.parent_id == None), backref="host")
    statistics = relation(statistic, primaryjoin = id == statistic.host_id, backref="host")
    last_crawled = Column(DateTime)
    crawl_time_in_s = Column(Integer)
    sharesize = Column(Numeric(precision=32, scale=0, asdecimal=True))
    
    def setIP(self, IP):
        self.ip_as_int = ipToInt(IP)
    
    def getIP(self):
	# fixed bug by explicit cast to int (ugly in my eyes)
        return intToIp(int(self.ip_as_int))
    
    def getPrettyShareSize(self):
        return makePretty(self.sharesize)
    
    ip = property(getIP, setIP)
    prettyShareSize = property(getPrettyShareSize)

    
