from paste.response import has_header
from paste.wsgilib import intercept_output

class ContentLengthMiddleware(object):
    """ this middleware allows you to set the Content-Length header field with streams by
        setting the virtual header field X-Content-Length to the desired value            """
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        status, headers, body = intercept_output(environ, self.app, start_response=start_response)
        for item in headers:
            if item[0] == 'X-Content-Length':
                headers.append(('Content-Length', str(item[1]) ))
                headers.remove(item)
            if item[0] == 'X-Content-Type':
                for entry in headers:
                    if entry[0] == 'Content-Type':
                        headers.remove(entry)
                headers.append(('Content-Type', str(item[1]) ))
                headers.remove(item)
        start_response(status, headers)
        return [body]
