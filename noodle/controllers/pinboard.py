# -*- coding: utf-8 -*-
"""Pinboard controller module"""

from datetime import datetime
from random import randrange

# turbogears imports
from tg import expose, tmpl_context, flash, redirect, url
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
                flash(u"Eintrag konnte nicht erstellt werden!", status="error")
            else:
                flash(u"Eintrag erstellt!", status="ok")
        
        # Get posts from database
        posts = DBSession.query(Post).order_by(Post.date.desc())
        # paginate handles all pagination-related functions, so we
        # don't have to do it on our own
        currentPage = paginate.Page(posts, page, items_per_page=20)
        
        # tmpl_context is used to get the form into the template
        tmpl_context.form = pinboard_form
        return dict(page="pinboard", posts=currentPage.items, currentPage=currentPage)

    @expose()
    def fill(self, num=25, author="Dummy"):
        dummytext = [u"Lorem ipsum...", u"Foo bar, foo, foo, bar, foobar, foo bar foo foofoo bar foobar", 
                     u"Wer andern eine Bratwurst brät, der hat ein Bratwurstbratgerät."]
        try:
            num = int(num)
            for i in range(num):
                newpost = Post()
                newpost.author = author
                newpost.text = dummytext[randrange(0, len(dummytext))]
                newpost.date = datetime.now()
                DBSession.add(newpost)
            transaction.commit()
        except Exception as e:
            transaction.abort()
            flash(u"Dummy-Einträge konnten nicht erstellt werden: %s" % e, status="error")
        else:
            flash(u"%d Dummy-Einträge erstellt!" % num, status="ok")
        redirect(url('/pinboard'))
