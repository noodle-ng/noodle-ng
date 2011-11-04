# -*- coding: utf-8 -*-
"""Download controller module"""
#TODO: smbc proxy downloading, propably by using the host class from the crawler
#TODO: Implement proxyDownloader with tg.controllers.WSGIAppController

# turbogears imports
from tg import expose, redirect, flash, request, override_template
from tg.decorators import use_custom_format
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from noodle.lib.base import BaseController
from noodle.model import DBSession, Share, File
from noodle.lib.utils import hasService, intToIp

class DownloadException(Exception):
    pass

class DownloadController(BaseController):
    """Handles all functionality related to proxydownloading"""
    
    @expose()
    def index(self, id=None):
        """Check parameters and return wsgi file app if possible
        
        Redirects to last page and flashes when there is an Exception
        """
        # This try..catch cascade performs some checks before the file app
        # is even loaded so that we don't waste too much time on folders
        # or other things we can't even download
        try:
            try:
                id = int(id)
            except ValueError as e:
                raise DownloadException(e)
            if not id:
                raise DownloadException("No file id specified")
            share = DBSession.query(Share).filter(Share.id==id).one()
            if not isinstance(share, File):
                raise DownloadException("Can only download files")
            if not hasService(intToIp(share.getHost().ip), share.getService().short_type):
                raise DownloadException("Host %s is not online" % share.getHost().name)
        except DownloadException as e:
            flash(u"Error: %s" % e, status="error")
            redirect(request.referrer)
        else:
            # As long as we don't have the file app here, we
            # just say what we WOULD have downloaded ;)
            flash(u"Downloading file %d" % id, status="ok")
            redirect(request.referrer)
