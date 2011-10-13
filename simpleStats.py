#try:
#    import pylab as pl
#except:
#    raise Exception("matplotlib missing: Install matplotlib to make this work! (you also should install X)")

import sys, os
from ConfigParser import SafeConfigParser
from noodle.model.share import Folder, File
from noodle.model import Host, Folder, File, Service, ServiceSMB, ServiceFTP, Crawl, before_commit
import noodle.model as model
from sqlalchemy.orm import sessionmaker, scoped_session, exc
from sqlalchemy import create_engine, event

# Some constant values
config_file = "crawler.ini"

config = SafeConfigParser({'here': sys.path[0]})
try:
    config.read(os.path.join(sys.path[0], config_file))
except:
    sys.exit("Could not read %s" % config_file)
    
url = config.get('main', 'sqlalchemy.url')
echo = config.getboolean('main', 'sqlalchemy.echo')

engine = create_engine(url, echo=echo)
model.maker = sessionmaker(bind=engine, autoflush=True, autocommit=False, extension=None)
model.DBSession = scoped_session(model.maker)
session = model.DBSession
        
# Register custom hooks
        
event.listen(session, "before_commit", before_commit)
event.listen(session, "before_flush", before_commit)

for host in session.query(Host).all():
    print host, host.ip, host.prettyShareSize