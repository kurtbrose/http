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

_DEFAULT_HEADERS = {
    "Accept-Encoding" : "identity",
    "User-Agent" : "Python HTTP"
}

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
        for k in _DEFAULT_HEADERS:
            self.headers.setdefault(k, _DEFAULT_HEADERS[k])
        
        self.bytes = "".join([ 
            self.method+" "+url+" HTTP/1.1\r\n",
            "\r\n".join(k+": "+v for k,v in self.headers.items),
            "\r\n",
            self.data #body of request
            ])
        

class Response(object):
    def __init__(self):
        self.code = -1
        self.message = None
        self.headers = {}
        self.body = ""
        self.state = "new"
        self._unparsed = [] #data which cannot yet be parsed (e.g. incomplete header)
        self._body_length = 0
    
    def parse(self, data):
        if self.state == "new": #step 1-- parse the http line
            status, sep, rest = data.partition("\r\n")
            if sep == '':
                self._unparsed.append(data)
                return
            else:
                data = rest
                status_line = "".join(self._unparsed) + status
                self._unparsed = []
                version, self.code, self.message = status_line.split()
                self.state = "headers"
        if self.state == "headers":
            headers, sep, body = data.partition("\r\n\r\n")
            if sep != '':
                self.state = "body"
                data = body
            headers = headers.split("\r\n") #TODO: what if last header is incomplete?
            if body == "" and headers[-1] != "": #last header was not complete
                self._unparsed.append(headers[-1])
            if self._unparsed:
                headers[0] = "".join(self.unparsed) + headers[0]
                self._unparsed = []
            for header in headers:
                name, _, value = header.partition(": ")
                self.headers[name] = value
        if self.state == "body":
            #first, append everything to _unparsed, then when the body is
            #complete, join all the stuff in _unparsed together
            self.body = data #TODO: length of body
    
    def needs_bytes(self):
        return self.state == "done"



