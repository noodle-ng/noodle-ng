# -*- coding: utf-8 -*-
"""The application's model objects"""
from datetime import datetime
from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import Integer, DateTime
from sqlalchemy import event, Column

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False,
                     extension=ZopeTransactionExtension())
DBSession = scoped_session(maker)

# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base()

# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata

# If you have multiple databases with overlapping table names, you'll need a
# metadata for each database. Feel free to rename 'metadata2'.
#metadata2 = MetaData()

#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
#
######

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    DBSession.configure(bind=engine)
    # If you are using reflection to introspect your database and create
    # table objects for you, your tables must be defined and mapped inside
    # the init_model function, so that the engine is available if you
    # use the model outside tg2, you need to make sure this is called before
    # you use the model.

    #
    # See the following example:

    #global t_reflected

    #t_reflected = Table("Reflected", metadata,
    #    autoload=True, autoload_with=engine)

    #mapper(Reflected, t_reflected)


def before_commit(session, flush_context=None, instances=None):
    #TODO: Docstring
    for instance in session.new:
        try:
            instance.created = datetime.now()
            instance.modified = datetime.now()
            instance.host_id = instance.getHost().id
        except:
            pass
    for instance in session.dirty:
        try:
            instance.modified = datetime.now()
            instance.host_id = instance.getHost().id
        except:
            pass
    for instance in session.deleted:
        pass

class BaseColumns():
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False)
    modified = Column(DateTime, nullable=False)

# Import your model modules here.
from noodle.model.share import Host, Service, Content, ServiceSMB, ServiceFTP, Share, Folder, File, getShareSum
from stats import Statistic, Ping, Crawl
#from noodle.model.meta import meta, metaAtom
from noodle.model.pinboard import Post
from noodle.model.search import search

event.listen(DBSession, "before_commit", before_commit)
event.listen(DBSession, "before_flush", before_commit)
