# -*- coding: utf-8 -*-
"""Search controller module"""
#TODO: Paging tutorial: http://turbogears.org/2.1/docs/modules/thirdparty/webhelpers_paginate.html#paginate-a-module-to-help-split-up-lists-or-results-from-orm-queries

# turbogears imports
from tg import expose
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from noodle.lib.base import BaseController
import noodle.model as model


class SearchController(BaseController):
    """Handles all the search related functionality"""
    
    @expose('noodle.templates.debug')
    def index(self, query, **kwargs):
        #TODO: Docstring
        kwargs['query'] = query
        s =  model.search(query)
        return dict(page='debug', params=kwargs, s=s)
        #return dict(page='debug', params=dict((k,v) for k,v in kwargs.iteritems() if v))
    
    def by_file(self):
        pass
    
    def by_host(self):
        pass
    
    def json(self):
        pass
    
    def xml(self):
        pass
