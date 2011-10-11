# -*- coding: utf-8 -*-

# this is the ONLY place where this import is allowed
from noodle.lib.iptools import ip2long , long2ip

# sockets for cross platform network methods
import socket as sk  

from urlparse import urlsplit, urlunsplit
from collections import namedtuple

port = {'smb': 445, 'ftp': 21}

#####################################################
# iptools wrapper (it makes sense to define a central
# place where the mapping is done, believe me!)
#####################################################

def ipToInt(ip):
    """ wraps ip2long method from iptools to noodle's api """
    
    # force explicit cast to ensure bitwise operations on it
    return int(ip2long(ip))

def intToIp(ip):
    """ wraps long2ip method from iptools to noodle's api """

    # force explicit cast to ensure bitwise operations on it
    return long2ip(int(ip))

#####################################################
# implement ping equivalent method for smb with 
# sockets to avoid external dependencies
############################sd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)#########################

def hasService(host, service, timeout=1):
    """checks if the given host is online and the port
    corresponding to service is open"""
    
    try:
        port[service]
    except KeyError:
        return False
    
    sd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    sd.settimeout(timeout)
    try:
        sd.connect((host, port[service]))
        sd.close()
        return True
    except:
        return False

def pingSMB(ip, timeout=1):
    """ checks if the given host is online and has a running smb server using pythons sockets"""
   
    sd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    sd.settimeout(timeout)
    try:
        sd.connect((ip, 445))
        sd.close()
        return 1
    except:
        return False
    
def getDnsEntry(ip):
    """ get the dns name for a given ip address """
    
    try:
        entry = sk.gethostbyaddr(ip)[0]
    except:
        entry = None
    return entry

def getHostByAddr(ip):
    """Returns hostname for ip address """
    try:
        host = sk.gethostbyaddr(ip)[0]
    except:
        host = None
    return host

def getHostByName(host):
    """Returns ip address for host"""
    try:
        ip = sk.gethostbyname(host)
    except:
        ip = None
    return ip

def getHostAndAddr(ip):
    """Returns hostname and ip address for ip address or host"""
    try:
        (name,alias,address) = sk.gethostbyaddr(ip)
        data = (name, address[0])
    except:
        data = (None, None)
    return data

#####################################################
# helper function that should be part of the
# standard library
#####################################################


def splitFileName(s):
    """ splits filename to (name, ext) 
    
    splits Kobe.avi to ('Kobe', 'avi') 
    splits .htaccess to ('', 'htaccess')
    splits file to ('file', '')
    """
    
    ret = s.rsplit('.', 1)
    name = ret[0]
    ext = ''
    
    if len(ret) == 2:
        ext = ret[1]
    
    return (name, ext)

def urlUnsplit(type, host, path, username=None, password=None):
    """urlUnsplit(*urlSplit("smb://hans@wurst/bude"))"""
    if username:
        if password:
            username = username + u":" + password
        host = username + u"@" + host
    return urlunsplit((type, host, path, u"", u""))

def urlSplit(url):
    """urlUnsplit(*urlSplit("smb://hans@wurst/bude"))"""
    UrlSplit = namedtuple("UrlSplit", ['scheme', 'hostname', 'path', 'username', 'password'])
    u = urlsplit(url)
    return UrlSplit(u.scheme, u.hostname, u.path, u.username, u.password)