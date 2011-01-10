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
VERBOSE = False

# Path definitions

# Wiĺl be used as root for the native os implementation
# and our reference implementation fs_os
LOCAL_TEST_ROOT = "/home/moschlar/"

# Wiĺl be used as root for the native os implementation
SMB_MOUNT_ROOT = ""
# Will be used as root uri for our implementation of fs_smb
SMB_TEST_URI = ""

import os
import fs_os as fs

def test(reference_path,test_path):
    # Generating reference list
    if DEBUG:
        print "reference test at %s" % reference_path
    reference_list = [x for x in os.walk(reference_path)]
    if VERBOSE:
        print "reference list:\n%s" % reference_list
    
    # Generating test list
    if DEBUG:
        print "test at %s" % test_path
    test_list = [x for x in fs.walk(test_path)]
    if VERBOSE:
        print "test list:\n%s" % test_list
    
    # Fastest test
    if not len(reference_list) == len(test_list):
        if DEBUG:
            print "lists not of same length"
        return False

    # This test could be also fast but since we do not rely on
    # the exact order of elements we should not use it too much
    if not str(reference_list) == str(test_list):
        if DEBUG:
            print "lists not of same string representation"
        return False

    # These are the most proper tests but the take some time
    # Of course, we want to make sure we have equality between the 
    # two lists so we have to check inclusions in both directions
    for i in range(0,len(reference_list)):
        if not reference_list[i] in test_list:
            if DEBUG:
                print "%s not in test_list" % reference_list[i]
            return False
        
    for i in range(0,len(test_list)):
        if not test_list[i] in reference_list:
            if DEBUG:
                print "%s not in reference_list" % test_list[i]
            return False

    # If we haven't already cancelled before, we're ok here
    return True

def main():
    if DEBUG:
        print "Now testing fs_os"
    #import fs_os as fs
            
    result = test(LOCAL_TEST_ROOT,LOCAL_TEST_ROOT)
    print result
    return result

if __name__ == '__main__':
    main()
