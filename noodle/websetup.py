# -*- coding: utf-8 -*-
"""Setup the Noodle-NG application"""

import logging

import transaction
from tg import config

from noodle.config.environment import load_environment

__all__ = ['setup_app']

log = logging.getLogger(__name__)


def setup_app(command, conf, vars):
    """Place any commands to setup noodle here"""
    load_environment(conf.global_conf, conf.local_conf)
    # Load the models
    from noodle import model
    print "Creating tables"
    model.metadata.create_all(bind=config['pylons.app_globals'].sa_engine)

    #testhost = model.share.host()
    #testhost.ip = "134.93.51.1"
    
    #service = model.share.service()
    #service.name = "smb"
    #service.host = testhost
    #testhost.services.append(service)
    
    #folder = model.share.folder()
    #folder.name = "testordner"
    #service.children.append(folder)
    
    #file = model.share.file()
    #file.name = "Kobe Tai"
    #file.extension = "avi"
    #file.size = 453523
    
    #file.parent = folder
    
    #model.DBSession.add(testhost)
    #model.DBSession.add(service)
    #model.DBSession.add(folder)
    
    transaction.commit()
    print "Successfully setup"
