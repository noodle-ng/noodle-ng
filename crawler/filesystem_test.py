#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""This script performs tests on the implementations of filesytems.

This test relies on the host operating systems capability of 
mounting the remote filesystem so we can access it with the os module
at its mountpoint.

ATM this script tests fs_os and fs_smb, because it's guaranteed that 
we can mount an smb share in the host os.
"""

# General options

# Enables output of results and specific errors
DEBUG = True
# Enables verbose output of paths, files and folders
VERBOSE = True

# Path definitions

# Wiĺl be used as root for the native os implementation
# and our reference implementation fs_os
LOCAL_TEST_ROOT = "/home/moschlar/Studium"

# Wiĺl be used as root for the native os implementation
SMB_MOUNT_ROOT = "/home/moschlar/Studium"
# Will be used as root uri for our implementation of fs_smb
SMB_TEST_URI = "smb://localhost/studium"

FTP_MOUNT_ROOT = "/home/moschlar/.gvfs/FTP auf dns320/public/eBooks"
FTP_TEST_URI = "ftp://dns320/public/eBooks"

import os
import fs_ftp as fs

def test(reference_path,test_path):
    # Generating reference list
    if DEBUG:
        print "reference test at %s" % reference_path
    reference_list = [(x.replace(reference_path,'',1),y,z) for (x,z,y) in os.walk(reference_path)]
    if VERBOSE:
        print "reference list:\n%s" % str(reference_list)
    
    # Generating test list
    if DEBUG:
        print "test at %s" % test_path
    test_list = [(x.replace(test_path,'',1),y,z) for (x,z,y) in fs.walk(test_path)]
    if VERBOSE:
        print "test list:\n%s" % str(test_list)
    
    # Fastest test
    if not len(reference_list) == len(test_list):
        if DEBUG:
            print "lists not of same length"
        return False

    # These are the most proper tests but the take some time
    # Of course, we want to make sure we have equality between the 
    # two lists so we have to check inclusions in both directions
    for entry in reference_list:
        if not entry in test_list:
            if DEBUG:
                print "%s not in test_list" % str(entry)
            return False
        if VERBOSE:
            print "found %s in test_list" % str(entry)
        
    for entry in test_list:
        if not entry in reference_list:
            if DEBUG:
                print "%s not in reference_list" % str(entry)
            return False
        if VERBOSE:
            print "found %s in reference_list" % str(entry)

    # If we haven't already cancelled before, we're ok here
    return True

def main():
    if DEBUG:
        print "Now testing fs_ftp"
    #import fs_os as fs
            
    result = test(FTP_MOUNT_ROOT,FTP_TEST_URI)
    print result
    return result

if __name__ == '__main__':
    main()
