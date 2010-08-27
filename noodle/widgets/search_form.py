# -*- coding: utf-8 -*-
"""Search Form"""

from tw.api import WidgetsList
from tw.forms import TableForm, CalendarDatePicker, SingleSelectField, RadioButtonList, TextField, TextArea, Spacer
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

class Generic(TableForm):
    """ generic file search form """

    class fields(WidgetsList):
        query   = TextField(label_text='Suche')
        Spacer()
        greater = TextField(label_text=u'groesser als', size=5, help_text='in MiB', default=0)
        smaller = TextField(label_text='kleiner als', size=5, help_text='in MiB', default=0)
        before  = CalendarDatePicker(label_text='aelter als', date_format="%d.%m.%Y", default="")
        after   = CalendarDatePicker(label_text='neuer als', date_format="%d.%m.%Y", default="")
        host    = TextField(label_text='Host')
        hostel  = Hostel(label_text='Wohnheim', disabled=True)
        ext     = TextField(label_text='Endung', size=4)
        type 	= Type(label_text='Typ')
    
    submit_text = 'noodle'


generic = Generic("Generic", action='search_by_host')
