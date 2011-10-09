# -*- coding: utf-8 -*-
'''
Created on 01.10.2011

@author: moschlar
'''
from tg import url
from tw.forms import TableForm, TextField, TextArea

class Pinboard(TableForm):
    
    fields = [
        TextField('author', label_text=u'Autor'),
        TextArea('text', attrs={'rows':10,'cols':30}),
        ]
    
    submit_text = u'Eintrag anheften'

pinboard_form = Pinboard('pinboard_form', action=url('/pinboard'), method="POST")
