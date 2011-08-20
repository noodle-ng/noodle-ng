#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import ConfigParser
import logging

import noodle.lib.utils as utils

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
    