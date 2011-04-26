#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ConfigParser
import logging

import noodle.lib.utils as utils

# this will be the new crawler
################################################################################
# global configuration which  should be definied somewhere else in the future
################################################################################

# login credentials
credentials = { 'Gast':'123Dabei', 'anonymous':'' }

################################################################################
# local configuration which can stay here
################################################################################

# smbc type shortcuts
smbc_type = { 'share':3, 'folder':7, 'file':8 }

# configuration file
config_file = 'production.ini'

config = ConfigParser.SafeConfigParser()
config.read(config_file)
url = config.get('app:main', 'sqlalchemy.url', raw = True)
if not url: raise

def main():
    '''
    '''
    
    parser = argparse.ArgumentParser(description='Starts the Noodle crawler')
    parser.add_argument('host', type=str, nargs='*')
    parser.add_argument('-v', '--version', action='version', version='Noodle NG Crawler ')
    args = vars(parser.parse_args())
    
    print(args)
    
    print(url)
    
    print(utils.splitFileName('Kobe.avi'))
    print(utils.pingSMB('127.0.0.1'))
    print(utils.getDnsEntry('127.0.0.1'))

if __name__ == '__main__':
    main()
    