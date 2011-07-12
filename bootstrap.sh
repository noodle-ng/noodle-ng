#!/bin/bash

# create virtual-env
virtualenv --no-site-packages tg2env
cd tg2env
source bin/activate

# install tg 2.0
easy_install -i http://www.turbogears.org/2.0/downloads/current/index tg.devtools
easy_install -i http://www.turbogears.org/2.0/downloads/current/index pysqlite

# pysmbc in correct version
wget http://cyberelk.net/tim/data/pysmbc/pysmbc-1.0.9.tar.bz2
easy_install pysmbc-1.0.9.tar.bz2
rm pysmbc-1.0.9.tar.bz2

# checkout noodle
svn checkout http://noodle-ng.googlecode.com/svn/trunk/ noodle-ng
cd noodle-ng
python setup.py develop

# deactivate virtual-env
deactivate

