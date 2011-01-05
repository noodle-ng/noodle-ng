#!/usr/bin/env python
# -*- coding: utf-8 -*-

# this will be the new crawler
################################################################################
# global configuration which  should be definied somewhere else in the future
################################################################################

#login credentials
credentials = {'Gast':'123Dabei','anonymous':''}

################################################################################
# local configuration which can stay here
################################################################################

# smbc type shortcuts
smbc_type={'share':3,'folder':7,'file':8}

################################################################################
# functions which should be sourced out to somewhere else in the future
################################################################################

def getDnsEntry(ip):
    """ get the dns name for a given ip address """
    
    # !!! EDIT THIS !!!
    # should this import be local or global in the future?
    import socket as sk
    
    try:
        entry = sk.gethostbyaddr(ip)[0]
    except:
        entry = None
    return entry

def splitFileName(s):
    """ splits Kobe.avi to 'Kobe' and 'avi' """
    
    name=''
    ext=''
    
    #reverse fileName s
    s=s[::-1]
    #if no dot in fileName s
    position=s.find('.')
    
    #if no dot in fileName s
    if position == -1 :
        name=s[::-1]
    #else split by dot
    else:
        ext=s[:position][::-1]
        name=s[position+1:][::-1]
    return [name,ext]