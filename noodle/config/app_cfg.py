# -*- coding: utf-8 -*-
"""
Global configuration file for TG2-specific settings in Noodle-NG.

This file complements development/deployment.ini.

Please note that **all the argument values are strings**. If you want to
convert them into boolean, for example, you should use the
:func:`paste.deploy.converters.asbool` function, as in::
    
    from paste.deploy.converters import asbool
    setting = asbool(global_conf.get('the_setting'))
 
"""

from tg.configuration import AppConfig

import noodle
from noodle import model
from noodle.lib import app_globals, helpers 

base_config = AppConfig()
base_config.renderers = []

base_config.package = noodle

#Enable json in expose
base_config.renderers.append('json')
#Set the default renderer
base_config.default_renderer = 'genshi'
base_config.renderers.append('genshi')
# if you want raw speed and have installed chameleon.genshi
# you should try to use this renderer instead.
# warning: for the moment chameleon does not handle i18n translations
#base_config.renderers.append('chameleon_genshi')

#Configure the base SQLALchemy Setup
base_config.use_sqlalchemy = True
base_config.model = model
base_config.DBSession = model.DBSession

#------------------------------------------------------------------------------
# Deprecated, these are now in app_globals

# Register handler for global template variables
#base_config.variable_provider = helpers.add_global_tmpl_vars
# Basic global values
#base_config.title = "Noodle NG"
#base_config.version = "1.5-alpha"
#base_config.subtitle = "File search engine"
