# -*- coding: utf-8 -*-
"""Download controller"""

# turbogears imports
from tg import expose, redirect, url, flash
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates

# project specific imports
from noodle.lib.base import BaseController
#from noodle.model import DBSession, metadata


class DownloadController(BaseController):
    
    @expose()
    def index(self,id=None):
        if not id:
            flash("File not found", status="error")
            redirect(url('/'))
        return "Downloading file with id %s" % id
