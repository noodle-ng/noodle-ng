# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect, config, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_

from noodle.lib.base import BaseController
from noodle.model import DBSession, metadata
from noodle import model

from noodle.controllers.error import ErrorController
from noodle.controllers.search import SearchController
from noodle.controllers.pinboard import PinboardController

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

    error = ErrorController()
    
    search = SearchController()
    pinboard = PinboardController()
    
    # If no _default is defined, a standard 404 Error message is displayed
#    @expose('noodle.templates.not_found')
#    def _default(self, *args, **kwargs):
#        return dict(page='not_found', args=args, kwargs=kwargs)

    advanced_search = search.advanced
    quicksearch = search.quick

    @expose('noodle.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

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

