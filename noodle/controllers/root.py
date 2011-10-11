# -*- coding: utf-8 -*-
"""Main Controller"""
import logging

from tg import expose, tmpl_context
#from tg import expose, flash, require, url, request, redirect, config, tmpl_context
#from tg.i18n import ugettext as _, lazy_ugettext as l_

from noodle.lib.base import BaseController
from noodle.model import DBSession, metadata, getShareSum
from noodle import model

from noodle.widgets import search_form,advanced_search_form

# Import sub-controllers
from noodle.controllers.error import ErrorController
from noodle.controllers.search import SearchController
from noodle.controllers.pinboard import PinboardController
from noodle.controllers.download import DownloadController

__all__ = ['RootController']

#TODO: Everything
#TODO: Error handling in Production

class RootController(BaseController):
    """
    The root controller for the Noodle-NG application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    # Register default error controller
    error = ErrorController()
    # Import sub-controllers
    search = SearchController()
    pinboard = PinboardController()
    download = DownloadController()
    
    
    # If no _default is defined, a standard 404 Error message is displayed by the ErrorController
#    @expose('noodle.templates.not_found')
#    def _default(self, *args, **kwargs):
#        return dict(page='not_found', args=args, kwargs=kwargs)
    
    
    @expose('noodle.templates.index')
    def index(self):
        """Handle the front-page."""
        tmpl_context.search_form=search_form
        sharesum = getShareSum()
        return dict(page='index', sharesum=sharesum)
    
    @expose('noodle.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')
    
    @expose('noodle.templates.faq')
    def faq(self):
        """Handle the 'faq' page"""
        return dict(page='faq')
    
    @expose('noodle.templates.contact')
    def contact(self):
        """Handle the 'contact' page."""
        return dict(page='contact')
    
    # Now there are two functions for the search pages
    
    @expose('noodle.templates.quicksearch')
    def quicksearch(self):
        """Handle the 'quicksearch' page."""
        return dict(page='quicksearch')
    
    @expose('noodle.templates.advanced_search')
    def advanced_search(self):
        """Handle the 'advanced_search' page."""
        # Get hostels from database for up-to-date information in the widget
        # Too specific for uni-mainz, propably okay if it was called superdomain or something similar
        #TODO: classmethod
        hostels = set([host.name.split('.')[1] for host in model.DBSession.query(model.Host).all()])
        tmpl_context.form = advanced_search_form
        return dict(page='advanced_search', hostels=hostels)
