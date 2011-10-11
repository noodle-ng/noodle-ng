# -*- coding: utf-8 -*-
"""Pinboard controller module"""

from datetime import datetime

# turbogears imports
from tg import expose, tmpl_context, flash
#from tg import redirect, validate, flash

# third party imports
#from tg.i18n import ugettext as _
#from repoze.what import predicates
from webhelpers import paginate

# project specific imports
from noodle.lib.base import BaseController
from noodle.model import DBSession, Post
import transaction
from noodle.widgets import pinboard_form

class PinboardController(BaseController):
    """Handles all pinboard related functionality"""
    
    @expose('noodle.templates.pinboard')
    def index(self, page=1, author=None, text=None):
        """Handles the pinboard page 
        
        which handles both viewing and writing of pinboard entries"""
        if author and text:
            try:
                # create new post
                newpost = Post()
                newpost.author = author
                newpost.text = text
                newpost.date = datetime.now()
                DBSession.add(newpost)
                transaction.commit()
            except:
                transaction.abort()
                flash("Eintrag konnte nicht erstellt werden!", status="error")
            else:
                flash("Eintrag erstellt!", status="ok")
        
        posts = DBSession.query(Post).order_by(Post.date.desc())
        currentPage = paginate.Page(posts, page, items_per_page=20)
        
        tmpl_context.form = pinboard_form
        return dict(page="pinboard", posts=currentPage.items, currentPage=currentPage)
