#!/usr/bin/env python3
from proxy2.proxy2 import *
from proxy2.https_trasparent import ThreadingHTTPSServer
from proxy2.https_trasparent import test as test_https

if __name__ == "__main__":
    # test(LLSIFmodifyRequestHandler, ThreadingHTTPServer)
    test_https(ProxyRequestHandler, ThreadingHTTPSServer)
