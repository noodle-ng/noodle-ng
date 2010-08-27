# Source: http://pythonpaste.org/webob/file-example.html
from webob import Request, Response
from webob.byterange import Range
import os
import logging

import smbc
buffersize = 4096 # 4KB
c = smbc.Context()

class FileApp(object):
    def __init__(self, uri):
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
    chunk_size = 4096
    def __init__(self, uri, start, stop):
        self.uri = uri
        self.fileobj = c.open(self.uri)

        if start:
            self.fileobj.seek(start)
        if stop is not None:
            self.length = stop - start + 2  # don't know why the response is 2 bits short.
                                            # need to look into that
        else:
            self.length = None
    def __iter__(self):
        return self
    def next(self):
        if self.length is not None and self.length <= 0:
             raise StopIteration
        chunk = self.fileobj.read(self.chunk_size)
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
    print uri
    
    f = c.open(uri)
    fs = f.fstat()
    filesize = fs[6]
    last_modified = fs[8] # mtime
    filename = uri.split("/")[-1]
    
    req = Request(environ)
    if req.range:
        # ranged transfer
        res.status_int = 206
        res.content_range = req.range.content_range(filesize)
        (start, stop) = req.range.ranges[0]
        if not stop:
            stop = filesize
        if not start:
            start = 0
        res.content_length = stop - start + 2
        res.app_iter = FileIterable(uri, start=start, stop=stop)
    else:
        # normal transfer
        res.content_length = filesize
        res.app_iter = FileIterable(uri)
    
    res.content_type='application/octet-stream'
    res.last_modified = last_modified
    res.etag = '%s-%s-%s' % (fs[8], fs[6], hash(f))
    res.headers.add('Content-Disposition', 'attachment; filename="%s"' % str(filename) )
    res.headers.add('Accept-Ranges', 'bytes')
    return res

