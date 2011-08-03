# TODO: Add more comments
# Source: http://pythonpaste.org/webob/file-example.html
from webob import Request, Response
from webob.byterange import Range
from webob.exc import HTTPOk, HTTPNotFound, HTTPGatewayTimeout
import os
import logging
from noodle.lib.utils import pingSMB

log = logging.getLogger("proxydl")

import smbc
c = smbc.Context()

# All these values were used for testing, but 16 KiB was the best
#chunk_size = 4096 # 4 KiB
chunk_size = 16384 # 16 KiB
#chunk_size = 32768 # 32 KiB
#chunk_size = 65536 # 64 KiB
#chunk_size = 131072 # 128 KiB
#chunk_size = 262144 # 256 KiB
#chunk_size = 524288 # 512 KiB
#chunk_size = 1048576 # 1 MiB

class FileApp(object):
    
    def __init__(self, uri):
        log.debug("init with uri: " + uri)
        self.uri = uri
    def __call__(self, environ, start_response):
        res = make_response(self.uri, environ)
        return res(environ, start_response)

class FileIterable(object):
    
    def __init__(self, uri, start=None, stop=None):
        self.uri = uri
        self.start = start
        self.stop = stop
    
    def __iter__(self):
        return FileIterator(self.uri, self.start, self.stop)
    
    def app_iter_range(self, start, stop):
        return self.__class__(self.uri, start, stop)

class FileIterator(object):
    
    def __init__(self, uri, start, stop):
        self.uri = uri
        self.fileobj = c.open(self.uri)
        log.debug("init FileIterator     start: " + str(start) + "   stop: " + str(stop))
        
        if start:
            self.fileobj.seek(start)
        if stop is not None:
            self.length = stop - start
        else:
            self.length = None
    
    def __iter__(self):
        return self.fileobj
    
    def next(self):
        #log.info("INTERATING")
        if self.length is not None and self.length <= 0:
             raise StopIteration
        chunk = self.fileobj.read(chunk_size)
        if not chunk:
            raise StopIteration
        if self.length is not None:
            self.length -= len(chunk)
            if self.length < 0:
                # Chop off the extra:
                chunk = chunk[:self.length]
        return chunk

def make_response(uri, environ):
    
    res = Response(conditional_response=True)
    
    # check if the host is online. If not raise an http error
    if not pingSMB( parseSMBuri(uri)["host"] ):
        return HTTPGatewayTimeout("Host is currently offline. You may try again at a later time.")
    
    try:
        f = c.open(uri)
    except smbc.NoEntryError:
        return HTTPNotFound("The file you requested is no longer available!")
    
    fs = f.fstat()
    filesize = fs[6]
    last_modified = fs[8] # mtime
    filename = uri.split("/")[-1]
    req = Request(environ)
    log.debug("Incoming request: \n" + str(req))
    
    if req.range:
        log.debug("begin ranged transfer")
        res.status_int = 206
        res.content_range = req.range.content_range(filesize)
        (start, stop) = req.range.range_for_length(filesize)
        
        log.debug("filesize: " + str(filesize))
        log.debug("start: " + str(start)  + "   stop: " + str(stop))
        log.debug("Content-Range: " + str(res.content_range))
        
        res.app_iter = FileIterable(uri, start=start, stop=stop)
        res.content_length = stop - start
    
    else:
        log.debug("begin normal transfer")
        res.app_iter = FileIterable(uri)
        res.content_length = filesize
    
    log.debug("Content-Length: " + str(res.content_length))
    
    res.server_protocol = "HTTP/1.1"
    # Make sure the file gets downloaded and not played live
    res.content_type = "application/octet-stream"
    res.last_modified = last_modified
    res.etag = '%s-%s-%s' % (fs[8], fs[6], hash(f))
    res.headers.add("Content-Disposition", 'attachment; filename="%s"' % str(filename) )
    res.headers.add("Accept-Ranges", "bytes")
    return res

def parseSMBuri(uri):
    """This function parses an smb uri
    It returns a dict of username,password,host
    """
    # uri scheme: smb://host/path or smb://username:password@host/path
    uri = uri.split("//")[1]
    uri_netloc = uri.split("/")[0]
    if "@" in uri_netloc:
        # ok, we have a uri with username:password@
        username = uri_netloc.split(":")[0]
        password = uri_netloc.split(":")[1][0:-1] #substract the @
        host = uri_netloc.split("@")[1]
    else:
        username = None
        password = None
        host = uri_netloc
    return dict(host=host, username=username, password=password)
