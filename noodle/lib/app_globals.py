# -*- coding: utf-8 -*-

"""The application's Globals object"""

__all__ = ['Globals']


class Globals(object):
    """Container for objects available throughout the life of the application.

    One instance of Globals is created during application initialization and
    is available during requests via the 'app_globals' variable.

    """

    def __init__(self):
        """Initialize global variables"""
        
        # Since these variables aren't meant to be changed in configuration
        # I'd like to keep them set here globally
        self.title = "Noodle NG"
        self.version = "1.5-alpha"
        self.subtitle = "File search engine"
        
        # The predefined quicksearches should propably be
        # configured in the .ini files
        self.quicksearch = [('dns320','host:dns320')]