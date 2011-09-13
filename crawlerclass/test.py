'''
Created on 05.09.2011

@author: moschlar
'''

path = u"smb://Gast:123Dabei@dns320/public/eBooks"

from crawler_smb import CrawlerSMB

crawlersmb = CrawlerSMB()

print crawlersmb.onewalk(path)
(dirs,files) = crawlersmb.onewalk(path)
print crawlersmb.listdir(path)
print crawlersmb.isdir(path)
print crawlersmb.isfile(path)
print crawlersmb.stat(path+"/"+files[0])