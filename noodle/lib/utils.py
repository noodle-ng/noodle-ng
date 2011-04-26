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
    """ Splits filename to (name, ext) 
    
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
