'''
Created on 12.10.2011

This module contains all search-related functions.

I strongly believe this belongs here, since even the keyword parsing
depends on currently available database fields and should be globally
in the Noodle-NG application.

@author: moschlar
'''

#DONE: Some keywords may be specified multiple times, e.g. host, ext, type?, (hostel)
#TODO: What if someone searches for "Kobe.avi"

from datetime import datetime

from sqlalchemy.orm import sessionmaker, scoped_session, exc
from sqlalchemy import create_engine, event

import noodle.model
from noodle.model import Share, Content, Host, File, Folder, DBSession as s

#===============================================================================
# magicwords = ["host", "type", "ext", "greater", "smaller", "before", "after", "found_before", "found_after", "hostel"]
# 
# mws = {"host": {"type": str, "multiple": True},
#       "type": {"type": str, "multiple": True},
#       "ext": {"type": str, "multiple": True},
#       "greater": {"type": int, "multiple": False}
#       }
#===============================================================================

#===============================================================================
# videoExt = [u"avi", u"mkv", u"mp4", u"mpv", u"mov", u"mpg", u"divx", u"vdr"]
# audioExt = [u"mp3", u"aac", u"ogg", u"m4a", u"wav"]
# mediaExt = videoExt + audioExt
#===============================================================================

extensions = {"video": [u"avi", u"mkv", u"mp4", u"mpv", u"mov", u"mpg", u"divx", u"vdr"],
              "audio": [u"mp3", u"aac", u"ogg", u"m4a", u"wav"]}
extensions["media"] = extensions["video"] + extensions["audio"]

filters = {"multiple": ["host", "ext", "hostel"],
           "single": ["type", "greater", "smaller", "before", "after", "found_before", "found_after"]}

def splitQuery(query):
    #TODO: Docstring
    #TODO: Should split query and respect quoted parts
    quotes = ["'", '"']
    return query.split()

def compileQuery(query):
    #TODO: Docstring
    result = {"query": []}
    for subquery in splitQuery(query):
        try:
            (mw, v) = subquery.split(':', 1)
            if mw in filters["single"] and v:
                if mw in result:
                    raise Exception("magic word %s specified multiple times" % mw)
                else:
                    result[mw] = v
            elif mw in filters["multiple"] and v:
                if mw in result:
                    result[mw].append(v)
                else:
                    result[mw] = [v]
            else:
                result["query"].append(subquery.strip())
        except ValueError:
            result["query"].append(subquery.strip())
    return result

def searchQuery(query):
    #TODO: Docstring
    query = compileQuery(query)
    
    #q = s.query(Content)
    q = Content.query
    if "type" in query and query["type"]:
        if query["type"] in ["file"] + extensions.keys():
            #q = s.query(File)#.filter(Content.type == "file")
            q = File.query
        elif query["type"] == "folder":
            #q = s.query(Folder)#.filter(Content.type == "folder")
            q = Folder.query
    
    # First perform simple numerical filters
    if "greater" in query and query["greater"]:
        try:
            q = q.filter(Content.size > int(query["greater"]))
        except ValueError as e:
            print e
    if "smaller" in query and query["smaller"]:
        try:
            q = q.filter(Content.size < int(query["smaller"]))
        except ValueError as e:
            print e
    
    # Then date-based filters
    if "before" in query and query["before"]:
        try:
            q = q.filter(Content.date < datetime.strptime(query["before"], "%d.%m.%Y"))
        except ValueError as e:
            print e
    if "after" in query and query["after"]:
        try:
            q = q.filter(Content.date > datetime.strptime(query["after"], "%d.%m.%Y"))
        except ValueError as e:
            print e
    
    if "found_before" in query and query["found_before"]:
        try:
            q = q.filter(Content.created < datetime.strptime(query["before"], "%d.%m.%Y"))
        except ValueError as e:
            print e
    if "found_after" in query and query["found_after"]:
        try:
            q = q.filter(Content.created > datetime.strptime(query["after"], "%d.%m.%Y"))
        except ValueError as e:
            print e
    
    
    if "host" in query and query["host"]:
        try:
            hosts = []
            for host in query["host"]:
                hosts.extend((s.query(Host.id).filter(Host.name.like('%%%s%%' % host)).all()))
                #hosts.extend((Host.query.filter(Host.name.like('%%%s%%' % host)).all()))
            q = q.filter(Content.host_id.in_([host.id for host in hosts]))
        except KeyError as e:
            print e
    
    ext = []
    if "ext" in query and query["ext"]:
        ext.extend(query["ext"])
    if "type" in query and query["type"]:
        if query["type"] in extensions:
            ext.extend(extensions[query["type"]])
    
    if len(ext) > 0:
        q = q.filter(File.extension.in_(ext))
    
    if "query" in query and query["query"]:
        for word in query["query"]:
            #TODO: Improve this
            q = q.filter(Content.name.like('%%%s%%' % word))
    
    return q

def search_by_host(query):
    """Perform search for query and return host-based results
    
    Returns a list of Host objects which each contain a
    list of results that contains folders which contain a
    list of results that contains items which match the
    search query.
    Note that this does *not* resemble any filesystem structure
    since it gets flattened to three levels (host -> folder -> contents)
    
    
    Although the objects in these list structures are full
    database backed objects from the model it is advised
    to simply use the pre-generated results lists for
    displaying search results
    """
    
    query = searchQuery(query)
    
    hosts = []
    # take all distinct host_ids from query result
    for h in query.from_self(Content.host_id).distinct().all():
        # put corresponding Host in list
        host = s.query(Host).filter(Host.id == h.host_id).one()
        # initialize list for subitems of host
        host.results = []
        
        # get all parent_ids on this host from query result
        for f in query.filter(Content.host_id == h.host_id).from_self(Share.parent_id).distinct():
            # get corresponding Folder
            folder = s.query(Share).filter(Share.id == f.parent_id).one()
            folder.showpath = folder.getShowPath()
            # initialize list for subitems of the folder
            folder.results = []
            
            # get all entries of folder
            for item in query.filter(Content.parent_id == folder.id).order_by(Content.name).all():
                item.showname = item.getShowName()
                folder.results.append(item)
            
            # prohibit adding empty folders
            if len(folder.results) > 0:
                host.results.append(folder)
        # prohibit adding empty hosts
        if len(host.results) > 0:
            hosts.append(host)

    return hosts

def search(query):
    return searchQuery(query).all()
    
