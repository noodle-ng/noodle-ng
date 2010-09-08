import socket as sk

############################################################
# some tools 
############################################################

def getDnsEntry(ip):
        """ get the dns name for a given ip address """
        try:
            entry = sk.gethostbyaddr(ip)[0]
        except:
            entry = None
        return entry
    

def isSmbServer(ip):
        """ looks for running samba server """
       
        # check if the server is running a smb server  // timeout 1s
        sd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
        sd.settimeout(1)
        try:
            sd.connect((ip, 445))
            sd.close()
            return True
        except:
            return False

	
