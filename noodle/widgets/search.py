# -*- coding: utf-8 -*-
'''
Created on 01.10.2011

@author: moschlar
'''
from tg import url
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, RadioButtonList, TextField, TextArea, Spacer, SubmitButton 

class Search(TableForm):
    
    type_options = ["", "audio", "video", "multimedia", "file", "folder"]
    search_mode_options = ["noodle by file", "noodle by host"]
    
    fields = [
        TextField('query', label_text=""),
#        Spacer(),
#        TextField('greater', label_text=u'größer als', size=5, help_text=u'in MiB', default=0),
#        TextField('smaller', label_text=u'kleiner als', size=5, help_text=u'in MiB', default=0),
#        Spacer(),
#        CalendarDatePicker('before', label_text=u'älter als', date_format="%d.%m.%Y", default=""),
#        CalendarDatePicker('after', label_text=u'neuer als', date_format="%d.%m.%Y", default=""),
#        CalendarDatePicker('found_before', label_text=u'gefunden vor dem', date_format="%d.%m.%Y", default="", width=500),
#        CalendarDatePicker('found_after', label_text=u'gefunden nach dem', date_format="%d.%m.%Y", default=""),
#        Spacer(),
#        TextField('host', label_text=u'Host'),
#        Spacer(),
#        TextField('ext', label_text=u'Endung', size=4),
#        SingleSelectField('type', label_text=u'Typ', options=type_options),
#        Spacer(),
#        RadioButtonList('mode', label_text=u'Suchmodus', options=search_mode_options, default=0),
        ]
    
    submit_text = u'noodle'

search_form = Search('search_form', action=url('/search'), method="GET")
