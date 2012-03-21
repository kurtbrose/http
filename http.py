#is it too labor intensive to create a Request and a Connection?
#http.post, http.get? -- no, that is the job of higher level library
#but, still can think of making it easy to implement

#if post and get are available, what of the Request and Response objects?
#the arguments could be so variable...

#who is responsible for constructing the Request and Response object?
#Connection should take a request and return a response


#example usage of the library:
def get(url, conn=None):
    if conn is None:
        if url.startswith("https"):
            conn = Connection(ssl.wrap_socket(socket.socket()))
        else:
            conn = Connection()
    return conn.do(Request(url, "GET"))

def post(url, data, conn=None):
    if conn is None:
        conn = Connection()
    return conn.do(Request(url, "POST", data))

#THE CODE ITESELF:
import socket

#could connection punt on HTTPS somehow?
class Connection(object):
    def __init__(self, socket=None, ):
        if socket is None:
            socket = socket.socket() #TODO: parameters
        self.busy = False
    
    #easier to ask forgiveness than permission -- this funciton is designed to
    #be cleanly re-entrant in case any WOULD_BLOCK exceptions get raised
    #
    #NOTE: do ssl.SSLSocket handle non-blocking okay?
    def do(self, request):
        self.busy = True
        
        if self._send_data is None:
            self._send_data = request.compose()
        
        while len(self._send_data) > 0:
            self.socket.send(self._send_data[:4096])
            self._send_data = self._send_data[4096:]
        
        if self._response is None:
            self._response = Response()
        
        while self._response.needs_bytes():
            self._response.parse(self.socket.recv())
        
        resp = self._response
        self._send_data = None
        self._response = None
        self.busy = False
        return resp

#is the job of a Request to "translate" the python data types to the bytes of
#an http request? this seems reasonable; in that case, should Response objects
#be parsers?

class Request(object):
    def __init__(self, url, method, headers=None, data=None):
        self.url = url
        self.method = method
        self.headers = headers
        self.data = data
    
    def compose(self):
        '''
        Return the bytes to be sent out on the wire
        '''
        pass
        

#a response can be a re-direct;
#what if the response is currently blocked and needs to be called again to
#continue?
#is that the job of this library to provide a continuation method?
#or, is that the job of lower level libraries?
#is this object just a dumb data-holder?
#should there be a separate parser object?
#should HTTP errors be raised as exceptions? or, is that just the data of the response?
class Response(object):
    def __init__(self):
        self.code = -1
        self.message = None
        self.headers = {}
        self.body = ""
    
    def parse(self, data):
        pass
    
    def needs_bytes(self):
        return self.state == "done"



