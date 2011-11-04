# -*- coding: utf-8 -*-
'''
Created on 12.10.2011

@author: moschlar
'''
# turbogears imports
from tg import expose
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from noodle.lib.base import BaseController
#from noodle.model import DBSession, metadata

#tg.controllers.WSGIAppController
from tg.controllers import WSGIAppController

#TODO: Test here what WSGIAppController can do 
# and if we could use it instead of the plain webob