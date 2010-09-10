# Source: http://pythonpaste.org/webob/file-example.html
from webob import Request, Response
from webob.byterange import Range
import os
import logging
log = logging.getLogger("proxydl")

import smbc
c = smbc.Context()

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
        log.info("init with uri: " + uri)
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
        log.info("init FileIterator     start: " + str(start) + "   stop: " + str(stop))
        
        if start:
            self.fileobj.seek(start)
        if stop is not None:
            self.length = stop - start
        else:
            self.length = None
    
    def __iter__(self):
        return self
    
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
    
    f = c.open(uri)
    fs = f.fstat()
    filesize = fs[6]
    last_modified = fs[8] # mtime
    filename = uri.split("/")[-1]
    #log.debug(environ)
    req = Request(environ)
    log.debug("Incoming request: \n" + str(req))
    
    if req.range:
        # We have some very strange values here!
        # WebOb gives us a wrong stop value, so we need to add 2 bytes
        # Then everything is fine!
        # Only `Range: bytes=-500` (the last 500 bytes) does not work, but that's not often used
        log.info("begin ranged transfer")
        res.status_int = 206
        res.content_range = req.range.content_range(filesize)
        (start, stop) = req.range.range_for_length(filesize)
        
        log.info("filesize: " + str(filesize))
        log.info("start: " + str(start)  + "   stop: " + str(stop))
        
        log.info("incoming bounds: start: " + str(start)  + "   stop: " + str(stop))
        if not stop:
            log.info("setting stop point")
            stop = filesize # because python excludes last byte
        else:
            stop = stop + 2
        
        if not start:
            log.info("setting start point")
            start = 0
        
        log.info("corrected bounds: start: " + str(start)  + "   stop: " + str(stop))
        
        log.info("Content-Range: " + str(res.content_range))
        
        res.app_iter = FileIterable(uri, start=start, stop=stop)
        
        res.content_length = stop - start
    
    else:
        log.info("begin normal transfer")
        res.app_iter = FileIterable(uri)
        res.content_length = filesize
    
    log.info("Content-Length: " + str(res.content_length))
    
    res.server_protocol = "HTTP/1.1"
    res.content_type = "application/octet-stream"
    res.last_modified = last_modified
    res.etag = '%s-%s-%s' % (fs[8], fs[6], hash(f))
    res.headers.add("Content-Disposition", 'attachment; filename="%s"' % str(filename) )
    res.headers.add("Accept-Ranges", "bytes")
    return res
