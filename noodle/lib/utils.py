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