# -*- coding: utf-8 -*-
"""Noodle pinboard model"""

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, DateTime

# TODO: Drop this import, so that genshi isn't needed for just using the crawler
from genshi.input import HTML

from noodle.model import DeclarativeBase, metadata, DBSession

class Post(DeclarativeBase):
    '''A pinboard post entry'''
    __tablename__ = 'pinboard'
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    author = Column(Unicode(32), nullable=False)
    text = Column(Unicode(2048), nullable=False)
    
    def escape(self):
        """Escape all potentially dangerous codes to HTML entities"""
        html_escape_table = {
            "\n": "<br />",
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return HTML("".join(html_escape_table.get(c, c) for c in self.text))
    
    escaped_text = property(escape)
