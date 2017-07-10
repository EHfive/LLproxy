from http.server import *
from http.client import *
import urllib.parse as urlparse

class ProxyHTTPRequestHandler(BaseHTTPRequestHandler):
    SERVER_HOST = 'prod.game1.ll.sdo.com'
    timeout = 20

    def proxy_request(self, method, url):
        httpconn = HTTPConnection(self.SERVER_HOST, timeout=self.timeout)
        httpconn.request(method, url)

    def do_GET(self):
        req = self
        content_length = int(req.headers.get('Content-Length', 0))
        req_body = self.rfile.read(content_length) if content_length else None

        print(self.request)
        self.send_header(self.headers)

        u = urlparse.urlsplit(req.path)
        scheme, netloc, path = u.scheme, u.netloc, (u.path + '?' + u.query if u.query else u.path)
        assert scheme in ('http',)
        if netloc:
            req.headers['Host'] = netloc

def test(serveclass=HTTPServer, handleclass=ProxyHTTPRequestHandler, address=('127.0.0.1', 8080)):
    myserver = serveclass(address, handleclass)
    myserver.serve_forever()

    input('Press Enter to continue...')
    myserver.shutdown()



test()