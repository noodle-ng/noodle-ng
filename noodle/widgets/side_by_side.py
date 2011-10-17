'''
Created on 17.10.2011

@author: moschlar
'''

from tw.forms import FieldSet

class SideBySide(FieldSet):
    """
    A fieldset that renders it's fields in a table side by side
    """
    template = "noodle.widgets.templates.side_by_side"

