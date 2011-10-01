# -*- coding: utf-8 -*-
"""Sample controller module"""
#TODO: Paging tutorial: http://turbogears.org/2.1/docs/modules/thirdparty/webhelpers_paginate.html#paginate-a-module-to-help-split-up-lists-or-results-from-orm-queries

# turbogears imports
from tg import expose, tmpl_context
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

from noodle.widgets import advanced_search_form

# project specific imports
from noodle.lib.base import BaseController
import noodle.model as model

class SearchController(BaseController):
    
    @expose('noodle.templates.search_debug')
    def index(self, **kwargs):
        return dict(page='search_debug', params=kwargs)
    
    @expose('noodle.templates.quicksearch')
    def quick(self):
        """Handle the 'quicksearch' page."""
        return dict(page='quicksearch')

    @expose('noodle.templates.advanced_search')
    def advanced(self):
        """Handle the 'advanced_search' page."""
        hostels = set([host.name.split('.')[1] for host in model.DBSession.query(model.Host).all()])
        tmpl_context.form = advanced_search_form
        return dict(page='advanced_search', hostels=hostels)