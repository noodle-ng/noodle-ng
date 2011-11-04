# -*- coding: utf-8 -*-
'''
Created on 01.10.2011

@author: moschlar
'''
from tg import url
from tw.forms import TableForm, FieldSet, CalendarDatePicker, SingleSelectField, RadioButtonList, TextField, TextArea, Spacer, SubmitButton 
from noodle.widgets.side_by_side import SideBySide

class Search(TableForm):
    """Display basic search field with submit button for both methods"""
    
    class SubmitButtons(SideBySide):
        """Using the side by side template to display the submit buttons"""
        fields = [
              SubmitButton('by_file', attrs=dict(name="by_file",value=u"Noodle by file")),
              SubmitButton('by_host', attrs=dict(name="by_host",value=u"Noodle by host"))
              ]
        # These attributes are simply put into the surrounding tags
        css_class = "center"
        attrs = dict(style="margin: 0px auto; text-align: center;")
    
    fields = [
        TextField('query', label_text="", size=60, attrs = dict(style="margin: 0px auto; text-align: center;")),
        SubmitButtons('submit')
        ]
    # We just want the plain search field and two buttons to search
    show_labels=False
    # Setting submit_text to None hides the standard submit button
    submit_text = None

# Initialize form object for easier access
search_form = Search('search_form', action=url('/search'), method="GET")
