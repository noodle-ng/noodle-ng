# -*- coding: utf-8 -*-
"""Search controller module"""
#TODO: Paging tutorial: http://turbogears.org/2.1/docs/modules/thirdparty/webhelpers_paginate.html#paginate-a-module-to-help-split-up-lists-or-results-from-orm-queries

import time

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
    
    @expose('noodle.templates.search_test')
    def test(self):
        """Perform some hardcoded search queries
        
        Displays plain search results and the time required for each.
        Kind of simple benchmarking.
        """
        results = []
        for query in ["hello world host:santa ext:clause ext:reindeer",
                      "du :sau ext:",
                      "greater:2 greater:3",
                      "greater: greater:2",
                      "before:12.12.2012",
                      "host:dns320 host:servant"]:
            try:
                start = time.time()
                s = model.search(query)
                stop = time.time()
            except Exception as e:
                results.append((query,0,e))
            else:
                results.append((query,stop-start,[]))
        return dict(page='test', results=results)
    
    def by_file(self):
        #TODO
        pass
    
    def by_host(self):
        #TODO
        pass
    
    def json(self):
        #TODO
        pass
    
    def xml(self):
        #TODO
        pass
