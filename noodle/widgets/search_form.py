# -*- coding: utf-8 -*-
"""Search Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, RadioButtonList, TextField, TextArea, Spacer, SubmitButton
#from tw.forms.validators import Int, NotEmpty, DateConverter

class Type(SingleSelectField):
    options = [
        "",
        "audio",
        "video",
        "multimedia",
        "file",
        "folder",
        ]
    
class Hostel(SingleSelectField):
    options = [
        "",
        "Oberstadt",
        "Weisenau",
        "K3",
		"Inter1",
		"Hechtsheim",
		"Wallstrasse",
        ]

class SearchMode(RadioButtonList):
    options = ["noodle by file", "noodle by host"]

class Generic(TableForm):
    """ generic file search form """

    class fields(WidgetsList):
        query   = TextField(label_text='Suche')
        Spacer()
        greater = TextField(label_text=u'größer als', size=5, help_text='in MiB', default=0)
        smaller = TextField(label_text=u'kleiner als', size=5, help_text='in MiB', default=0)
        before  = CalendarDatePicker(label_text=u'älter als', date_format="%d.%m.%Y", default="")
        after   = CalendarDatePicker(label_text=u'neuer als', date_format="%d.%m.%Y", default="")
        found_before  = CalendarDatePicker(label_text=u'gefunden vor dem', date_format="%d.%m.%Y", default="", width=500)
        found_after   = CalendarDatePicker(label_text=u'gefunden nach dem', date_format="%d.%m.%Y", default="")
        host    = TextField(label_text=u'Host')
        hostel  = Hostel(label_text=u'Wohnheim', disabled=True)
        ext     = TextField(label_text=u'Endung', size=4)
        type 	= Type(label_text=u'Typ')
        mode    = SearchMode(label_text=u'Suchmodus', default=0)
    
    submit_text = 'noodle'


generic = Generic("Generic", action='search')
