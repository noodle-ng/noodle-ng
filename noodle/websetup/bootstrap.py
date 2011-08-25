# -*- coding: utf-8 -*-
"""Setup the Noodle-NG application"""

import logging
from tg import config
from noodle import model

import transaction


def bootstrap(command, conf, vars):
    """Place any commands to setup noodle here"""

    # <websetup.bootstrap.before.auth

    # <websetup.bootstrap.after.auth>
