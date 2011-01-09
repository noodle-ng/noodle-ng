
import os

path = "/home/moschlar/Downloads"

print "path: %s" % path
print ""
print "##################################################################"
print ""

data = ("data")

def fstats(dirname,filename):
    stat = os.stat(dirname+"/"+filename)
    print filename
    print "Size: %s" % stat[6]

def visitor(data,dirname,files):
    #print "data: %s" % data
    print "dirname: %s" % dirname
    print "entries: %s" % files
    for file in files:
        fstats(dirname,file)
    return

os.path.walk(path,visitor,data)

for blob in os.walk(path):
    print blob

print ""
print "##################################################################"
print ""

import fs_os

def fstats(dirname,filename):
    stat = fs_os.stat(dirname+"/"+filename)
    print filename
    print "Size: %s" % stat[6]

fs_os.path_walk(path,visitor,data)

for blob in fs_os.walk(path):
    print blob

print ""
print "##################################################################"
print ""

import fs_smb

path = "smb://mopad/Downloads"

def fstats(dirname,filename):
    stat = fs_smb.stat(dirname+"/"+filename)
    print filename
    print "Size: %s" % stat[6]

fs_smb.path_walk(path,visitor,data)

for blob in fs_smb.walk(path):
    print blob
