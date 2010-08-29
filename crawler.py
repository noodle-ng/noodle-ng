
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# smb and dns methods
import noodleLib as n


# getting database url from production.ini
try:
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    #config.read('development.ini')
    config.read('production.ini')
    url = config.get('app:main','sqlalchemy.url',raw=True)
    if not url: raise
except:
    url = 'sqlite:///%(here)s/somedb.db'

print n.getDnsEntry('google.de') , n.isSmbServer('google.de')
