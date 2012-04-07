import http

GOOGLE_HTTP_RESPONSE = \
"""

"""

def test():
    resp = http.Response()
    resp.parse()


def raw_response_data(url):
    pass


#example usage of the library:
def get(url, conn=None):
    if conn is None:
        if url.startswith("https"):
            conn = http.Connection(ssl.wrap_socket(socket.socket()))
        else:
            conn = http.Connection()
    
    return conn.do(http.Request("GET", url))

def post(url, data, conn=None):
    if conn is None:
        conn = Connection()
    return conn.do(http.Request(url, "POST", data))


def basic_test():
    get("http://google.com")