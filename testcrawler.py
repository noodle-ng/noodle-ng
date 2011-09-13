'''
Created on 12.09.2011

@author: moschlar
'''
import sys, time
from noodle.lib.utils import urlSplit
from crawlerclass import CrawlerSMB, CrawlerFTP

if __name__ == "__main__":
    path = u"smb://Gast:123Dabei@dns320/public/eBooks"
    u = urlSplit(path)
    t1 = time.time()
    try:
        crawlersmb = CrawlerSMB(None,u.hostname,(u.username,u.password))
    except Exception, e:
        print e
        sys.exit(1)
    
    print crawlersmb.onewalk(u.path)
    (dirs,files) = crawlersmb.onewalk(u.path)
    print crawlersmb.listdir(u.path)
    print crawlersmb.isdir(u.path)
    print crawlersmb.isfile(u.path)
    print crawlersmb.stat(u.path+u"/OSP_wrobel_gentoo.pdf")
    
    t2 = time.time()
    
    try:
        crawlerftp = CrawlerFTP(None,u.hostname,(u.username,u.password))
    except Exception, e:
        print e
        sys.exit(1)
    
    print crawlerftp.onewalk(u.path)
    (dirs,files) = crawlerftp.onewalk(u.path)
    print crawlerftp.listdir(u.path)
    print crawlerftp.isdir(u.path)
    print crawlerftp.isfile(u.path)
    print crawlerftp.stat(u.path+u"/OSP_wrobel_gentoo.pdf")
    
    t3 = time.time()
    
    print "SMB took %f" % (t2-t1)
    print "FTP took %f" % (t3-t2)
    