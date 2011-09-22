'''
Created on 05.09.2011

@author: moschlar
'''
import fs_ftp as fs

path = "ftp://Gast:123Dabei@dns320/public/eBooks"

#for dir in fs.walk(path):
#    print dir

print fs.listdir(path)
print fs.isdir(path+"/EBooks")
print fs.isfile(path+"/EBooks")