#!/usr/bin/env python
# -*- coding: utf-8 -*-

import noodle.lib.utils as utils

# this will be the new crawler
################################################################################
# global configuration which  should be definied somewhere else in the future
################################################################################

#login credentials
credentials = {'Gast':'123Dabei','anonymous':''}

################################################################################
# local configuration which can stay here
################################################################################

# smbc type shortcuts
smbc_type={'share':3,'folder':7,'file':8}

print utils.splitFileName('Kobe.avi')
print utils.pingSMB('127.0.0.1')
print utils.getDnsEntry('127.0.0.1')