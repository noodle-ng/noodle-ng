'''
Created on 12.10.2011

This module contains all search-related functions.

I strongly believe this belongs here, since even the keyword parsing
depends on currently available database fields and should be globally
in the Noodle-NG application.

@author: moschlar
'''

import re

import noodle.model
from noodle.model import DBSession as s, Share, Host

magicwords = ["host", "type", "ext", "greater", "smaller", "before", "after", "found_before", "found_after", "hostel"]

def splitQuery(query):
    #TODO: Docstring
    #TODO: Should split query and respect quoted parts
    quotes = ["'", '"']
    return query.split()

def compileQuery(query):
    #TODO: Docstring
    result = {"query": ""}
    for subquery in splitQuery(query):
        try:
            (mw, v) = subquery.split(':', 1)
            if mw in magicwords and v:
                result[mw] = v
        except ValueError:
            result['query'] += "%s " % subquery.strip()
    return result

def searchQuery(query):
    #TODO: Docstring
    query = compileQuery(query)
    q = s.query(Share)
    try:
        print [host.id for host in s.query(Host).filter(Host.name.like('%%%s%%' % query['host'])).all()]
        q = q.filter(Share.host_id.in_([host.id for host in s.query(Host).filter(Host.name.like('%%%s%%' % query['host'])).all()]))
    except KeyError:
        pass
    return q

def search(query):
    return searchQuery(query).all()
    