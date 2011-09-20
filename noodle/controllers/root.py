# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from tg.i18n import ugettext as _, lazy_ugettext as l_

from noodle.lib.base import BaseController
from noodle.model import DBSession, metadata
from noodle import model

from noodle.controllers.error import ErrorController

__all__ = ['RootController']

#TODO: Everything
#TODO: Split up controllers a little bit 
#      (e.g. SearchController, DownloadController, etc)
#TODO: Error handling in Production
#TODO: Paging tutorial: http://turbogears.org/2.1/docs/modules/thirdparty/webhelpers_paginate.html#paginate-a-module-to-help-split-up-lists-or-results-from-orm-queries


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

    @expose('noodle.templates.index')
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('noodle.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('noodle.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ)

    @expose('noodle.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)

