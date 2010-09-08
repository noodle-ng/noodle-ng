import socket as sk

############################################################
# some tools to ensure the dry principle 
############################################################

#--- network related methods -------------------------------
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

def ipToInt(IP):
    ''' 255.255.255.255 => 4294967295 '''
    IntIP=0
    count=3
    for i in IP.split("."):
        if i!='0':
            IntIP+=int(i)*256**count
        count-=1           
    return IntIP

def intToIp(IntIP):
    IP=""
    for i in [(int(IntIP) & item[0]) >> 8*item[1] for item in [[255 << 8*k,k] for k in xrange(3,-1,-1)]]:
        IP+=str(i)+"."
    return IP[:-1]


#--- file related methods --------------------------
	
def makePretty(value):
    ''' convert bit values in human readable form '''
    steps = [ (1024,"KiB"), (1048576, "MiB"), (1073741824, "GiB"), (1099511627776, "TiB") ]
    for step in steps:
        m = step[0]
        suffix = step[1]
        try:
            cs = value / m
        except:
            return ""
        if cs < 10:
            return "%3.1f" % (cs) + ' ' + suffix
        if cs < 1024:
            return unicode( int(cs) ) + ' ' + suffix
    return "very big"
