# -*- coding: utf-8 -*-

"""WebHelpers used in Noodle-NG."""

from webhelpers import date, feedgenerator, html, number, misc, text

def add_global_tmpl_vars():
    """Register global template variables that are available
    in every template"""
    quicksearch = [('bla','blubb')]
    return dict(quicksearch=quicksearch)
