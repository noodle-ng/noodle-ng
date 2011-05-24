import socket as sk

############################################################
# some tools to ensure the DRY principle 
############################################################

#--- network related methods -------------------------------

def getDnsEntry(ip):
    """ gets the dns name for a given ip address """
    
    try:
        entry = sk.gethostbyaddr(ip)[0]
    except:
        entry = None
    return entry

def isSmbServer(ip):
    """ looks for running samba server """
   
    # check if the server is running a smb server
    sd = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    sd.settimeout(1)
    try:
        sd.connect((ip, 445))
        sd.close()
        return True
    except:
        return False

def ipToInt(IP):
    """ converts an IPv4 address to an integer (bijective)
    
    e.g. 255.255.255.255 => 4294967295 """
    
    IntIP = 0
    count = 3
    for i in IP.split("."):
        if i != '0':
            IntIP += ( int(i)*256 )**count
        count -= 1           
    return IntIP

def intToIp(IntIP):
    """ converts an integer to an IPv4 address (inverse function of ipToInt 
    
    e.g. 4294967295 => 255.255.255.255"""
    
    IP=""
    for i in [(int(IntIP) & item[0]) >> 8*item[1] for item in [[255 << 8*k,k] for k in xrange(3,-1,-1)]]:
        IP += str(i) + "."
    return IP[:-1]

def intToIp2(ip):
    """ 
    converts an integer to an IPv4 address (inverse function of ipToInt 
    e.g. 4294967295 => 255.255.255.255
    """
    
    result=[]
    for count in range(4):
        result.insert(0,str(ip%256))
        ip/=256

    return ".".join(result)

#--- file related methods --------------------------

def makePretty(value):
    """ converts file sizes from bit values to a human readable form """
    
    steps = [ (1024, "KiB"), 
              (1048576, "MiB"),
              (1073741824, "GiB"),
              (1099511627776, "TiB") ]
    
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
    return "too much"

if __name__ == "__main__":
    print intToIp(1323000)
    print intToIp2(1323000)
