# -*- coding: utf-8 -*-
"""Noodle meta model"""

# CURRENTLY UNUSED

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation, backref
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Binary, Float

from noodle.model import DeclarativeBase, metadata, DBSession

class meta(DeclarativeBase):
    __tablename__ = 'meta'
    id = Column(Integer, primary_key=True)
    share_id = Column(Integer, ForeignKey('shares.id'), nullable=False)
    atoms = relation("metaAtom", backref="meta")
    title = Column(Unicode(128))
    artist = Column(Unicode(128))
    album = Column(Unicode(128))
    date = Column(DateTime)
    comment = Column(Unicode(1024))
    genre = Column(Unicode(128))
    length = Column(Float())

class metaAtom(DeclarativeBase):
    __tablename__ = 'meta_atoms'
    id = Column(Integer, primary_key=True)
    meta_id = Column(Integer, ForeignKey('meta.id'), nullable=False)
    type = Column(Unicode(20), nullable=False)
    __mapper_args__ = {'polymorphic_on': type}

class metaVideo(metaAtom):
    __tablename__ = 'meta_video'
    id = Column(Integer, ForeignKey('meta_atoms.id'), primary_key=True)
    xres = Column(Integer)
    yres = Column(Integer)
    bitrate = Column(Integer)
    codec = Column(Unicode(20))
    fps = Column(Float())
    __mapper_args__ = {'polymorphic_identity': 'video'}

class metaAudio(metaAtom):
    __tablename__ = 'meta_audio'
    id = Column(Integer, ForeignKey('meta_atoms.id'), primary_key=True)
    bitrate = Column(Integer)
    rate = Column(Integer)
    language = Column(Unicode(20))
    channels = Column(Integer)
    codec = Column(Unicode(20))
    __mapper_args__ = {'polymorphic_identity': 'audio'}

class metaPicture(metaAtom):
    __tablename__ = 'meta_picture'
    id = Column(Integer, ForeignKey('meta_atoms.id'), primary_key=True)
    xres = Column(Integer)
    yres = Column(Integer)
    codec = Column(Unicode(20))
    data = Column(Binary())
    __mapper_args__ = {'polymorphic_identity': 'picture'}