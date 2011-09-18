'''
Imports the needed modules for interactively accessing the noodle model

Created on 18.09.2011

@author: moschlar
'''
import os, sys, time, datetime, logging, traceback
from noodle.lib.utils import *
from ConfigParser import SafeConfigParser

import transaction
import sqlalchemy
from sqlalchemy.orm import sessionmaker, scoped_session

import noodle.model as model

from noodle.model import *

# Some constant values
config_file = "crawler.ini"

# Parsing the overall configuration

config = SafeConfigParser({'here': sys.path[0]})
try:
    config.read(os.path.join(sys.path[0], config_file))
except:
    sys.exit("Could not read %s" % config_file)

debug = config.getboolean('main', 'debug')
if debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.WARNING)
processes = config.getint('main', 'processes')

sqlalchemy_url = config.get('main', 'sqlalchemy.url')
sqlalchemy_echo = config.getboolean('main', 'sqlalchemy.echo')


engine = sqlalchemy.create_engine(sqlalchemy_url, echo=sqlalchemy_echo)
#model.maker = sessionmaker(autoflush=False, autocommit=False, extension=model.MySessionExtension())
#model.DBSession = scoped_session(model.maker)
model.init_model(engine)
#model.metadata.create_all(engine)

session = model.DBSession()
