# -*- coding: utf-8 -*-
"""Main Controller"""

from datetime import datetime

from tg import expose, flash, require, url, request, response, redirect, tmpl_context #validate
from pylons.i18n import ugettext as _, lazy_ugettext as l_

from noodle.lib.base import BaseController
from noodle.model import DBSession, metadata
from noodle.controllers.error import ErrorController
import noodle.widgets.search_form as search_form

import noodle.model.share as s
from noodle.model.share import ipToInt, intToIp

from sqlalchemy.sql.expression import distinct
from sqlalchemy import or_, and_

import subprocess
import shlex

__all__ = ['RootController']

videoExt = ["avi", "mkv", "mp4", "mpv", "mov", "mpg", "divx"]
audioExt = ["mp3", "aac", "ogg", "m4a"]

mediaExt = videoExt[:]
mediaExt.extend(audioExt)

class RootController(BaseController):
    """
    The root controller for the Noodle-NG application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example:

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """

    error = ErrorController()

    @expose('noodle.templates.index')
    def index(self):
        """Handle the front-page."""

        #Calculates the overall share amount
        overallShare = 0
        for host in DBSession.query(s.host).all():
            if host.sharesize > 0:
                overallShare += host.sharesize

        #Renders the page index with overall share amount and changelog
        return dict(page='index', overallShare=s.makePretty(overallShare), changelog=True)

    @expose('noodle.templates.advanced_search')
    def advanced_search(self):
        """Displays the advanced search page"""
        tmpl_context.generic_search = search_form.Generic("Generic", action='search_by_host')
        return dict(page='advanced_search')

    @expose('noodle.templates.faq')
    def faq(self):
        """Displays the faq/help page"""
        return dict(page='faq', videoExt=videoExt, audioExt=audioExt, mediaExt=mediaExt)

    @expose('noodle.templates.contact')
    def contact(self):
        """Displays contact page"""
        return dict(page='contact')

    @expose('noodle.templates.search_by_host')
    def search_by_host(self, query=None, offset=0, length=10, cutoff=25, **kw):
        """Handle the 'search_by_host' page."""

        #Process keywords
        query += processKW(kw)["query"]

        offset = int(offset)
        length = int(length)

        if "MSIE" in request.user_agent:
            userAgent = "internetExplorer"
        else:
            userAgent = "mozilla"

        q = search(query)

        numberOfHosts = len( q.from_self(s.share.host_id).distinct().all() )
        pages = []
        i = 0
        n = 1
        while i <= numberOfHosts:
            pages.append({})
            pages[-1]["number"] = n
            pages[-1]["offset"] = i
            pages[-1]["current"] = offset == i
            n += 1
            i += length

        hosts = []
        for line in q.from_self(s.share.host_id).distinct()[offset:length+offset]:
            hosts.append( DBSession.query(s.host).filter(s.host.id == line[0]).first() )
            hosts[-1].resultset = [] # will be filled with the results later on
            if userAgent == "internetExplorer":
                hosts[-1].path = "\\\\" + str(hosts[-1].ip)
            else:
                hosts[-1].path = "smb://" + str(hosts[-1].ip)

        for host in hosts:
            for folderid in q.filter(s.share.host_id == host.id).from_self(s.share.parent_id).distinct()[:cutoff]: # cause the content.host value is only set for the first level we go for the id
                folder = DBSession.query(s.share).filter(s.share.id == folderid[0]).first()
                path = generatePath(folder, userAgent)
                folder.path = path
                folder.showpath = folder.getShowPath()
                folder.resultset =[]
                for item in q.filter(s.share.parent_id == folderid[0]).order_by(s.share.name).all():
                    item.path = path
                    if hasattr(item, "extension"):
                        if item.extension != None:
                            item.showname = item.name + u"." + item.extension
                        else:
                            item.showname = item.name
                    else:
                        item.showname = item.name
                    folder.resultset.append(item)
                host.resultset.append(folder)

        return dict(page='search', hosts=hosts, compiledQuery=q, query=query, offset=offset, lenght=length, pages=pages, numberOfHosts=numberOfHosts)

    @expose('noodle.templates.hostinfo')
    def hostInfo(self, hostID):
        host = DBSession.query(s.host).filter(s.host.id == hostID).first()
        return dict(page='hostinfo', host=host)

    @expose('noodle.templates.shareinfo')
    def shareInfo(self, shareID):
        share = DBSession.query(s.share).filter(s.share.id == shareID).first()
        return dict(page='hostinfo', share=share)

    @expose('noodle.templates.browseHost')
    def browseHost(self, hostID):
        return dict(page='BrowseHost')

    @expose('json')
    def getShare(self, shareID):
        share = DBSession.query(s.share).filter(s.share.id == shareID).first()
        return dict(share=share)

    @expose('json')
    def ping(self, ip=False):
        host = DBSession.query(s.host).filter(s.host.ip_as_int == ipToInt(ip)).first()
        result = systemPing(ip)
        if host:
            DBSession.add(s.ping(host, result))
            DBSession.commit()
        return dict(page='ping', time=result, host=ip)
    
    @expose()
    def proxyDownload(self, id, tar=False):
        
        # get path to file with ID id from database
        item = DBSession.query(s.share).filter(s.share.id == id).one()
        host = item.getHost()
        service = item.getService()
        filename = str( item.getShowPath().split("/")[-1] )
        
        if service.username and service.username != "anonymous":
            # uri = "smb://username:password@hostip/path/to/file"
            uri = u"smb://%s:%s@%s%s" % ( service.username, service.password, host.ip, item.getShowPath() )
        else:
            # uri = "smb://hostip/path/to/file"
            uri = u"smb://%s%s" % ( host.ip, item.getShowPath() )
        
        # see if the host is online
        if not systemPing(host.ip):
            raise
        
        import noodle.lib.smbfileapp as smbfileapp
        f = smbfileapp.FileApp(uri)
        from tg import use_wsgi_app
        return use_wsgi_app(f)

def search(query=None):
    """ process the query string and return a compiled query """
    fileExtensions = []
    onlyHosts = []  # search only these hosts
    q = DBSession.query(s.share)
    for subquery in query.split(" "):

        if subquery == "":
            continue

        negate = False
        if subquery[0:1] == "-":
            negate = True
            subquery = subquery[1:]

        if len(subquery.split(":")) == 2:
            operator, value = subquery.split(":")
            if operator == "ext":
                fileExtensions.append(value)
                continue
            if operator == "type":
                if value == "video":
                    fileExtensions.extend(videoExt)
                if value == "audio":
                    fileExtensions.extend(audioExt)
                if value == "multimedia":
                    fileExtensions.extend(mediaExt)
                if value == "file":
                    q = q.filter(s.share.type == "file")
                if value == "folder":
                    q = q.filter(s.share.type == "folder")
                continue
            if operator == "greater":
                size = int(value) * 1000000 # in MB
                q = q.filter( s.file.size > size )
                continue
            if operator == "smaller":
                size = int(value) * 1000000 # in MB
                q = q.filter( s.file.size < size )
                continue
            if operator == "before":
                date = datetime.strptime(value, "%d.%m.%Y")
                q = q.filter(s.share.date <= date)
                continue
            if operator == "after":
                date = datetime.strptime(value, "%d.%m.%Y")
                q = q.filter(s.share.date >= date)
                continue
            if operator == "host":
                onlyHosts.append(value)
                continue
            if operator == "hostid":
                q = q.filter( s.share.host_id == int(value) )
                continue

        if negate:
            q = q.filter(~s.share.name.like('%%%s%%' % subquery))
        else:
            q = q.filter(s.share.name.like('%%%s%%' % subquery))

    if len(fileExtensions) > 0:
        q = q.filter( s.file.extension.in_(fileExtensions) )

    if len(onlyHosts) > 0:
        onlyHostIDs = []
        for host in onlyHosts:
            for occurence in DBSession.query(s.host).filter(s.host.name.like('%%%s%%' % host)).all():
                onlyHostIDs.append(occurence.id)
        q = q.filter( s.share.host_id.in_(onlyHostIDs) )

    q = q.filter(s.share.type != "serviceSMB")
    return q

def processKW(kw):
    """ process the Keyword List and return a new kw and a query string """
    query = ""
    magic_words = ["greater", "smaller", "host", "type", "before", "after", "ext"]

    for mw in magic_words:
        if mw in kw:
            if kw[mw] <> None and kw[mw] <> "" and kw[mw] <> 0 and kw[mw] <> "0": # mw not empty
                query += " " + str(mw) + ":" + str(kw[mw])

    return dict(kw=kw, query=query)

def generatePath(obj, userAgent):
    if userAgent == "internetExplorer":
        return '\\\\' + obj.getPath()
    else:
        return "smb://" + obj.getPath()

def systemPing(ip):
    """ checks if the given host is online and has a running smb server using pythons sockets"""
    import commands
    import socket as sk

    sd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    sd.settimeout(1)
    try:
        sd.connect((ip, 445))
        sd.close()
        return 1
    except:
        return False
