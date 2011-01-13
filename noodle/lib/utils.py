# -*- coding: utf-8 -*-

def pingSMB(ip, timeout=1):
    """ checks if the given host is online and has a running smb server using pythons sockets"""
    import commands
    import socket as sk

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