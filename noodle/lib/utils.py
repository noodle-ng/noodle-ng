# -*- coding: utf-8 -*-

# this is the ONLY place where this import is allowed
from noodle.lib.iptools import ip2long , long2ip

# sockets for cross platform network methods
import socket as sk  

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
#####################################################

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
