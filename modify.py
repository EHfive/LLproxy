#!/usr/bin/env python3
from collections import OrderedDict
from datetime import datetime
from proxy2.proxy2 import *
from proxy2.https_trasparent import ThreadingHTTPSServer
from proxy2.https_trasparent import test as test_https
from LLConnectionDataHandler import *
import queue
import threading
import urllib.parse as urlparse
import json
from gen_xmessagecode import gen_xmessagecode
import config as cfg

host = ['prod.game1.ll.sdo.com', 'mgame.sdo.com']
nothandle = ['/webview.php', '/main.php/resources', '/main.php/notice', '/main.php/eventscenario',
             '/main.php/personalnotice', '/main.php/tos', '/main.php/subscenario', '/main.php/secretbox/all']
nothandle_api = ['rewardList', ]
q = queue.Queue()


class LLSIFmodifyRequestHandler(ProxyRequestHandler):
    def request_handler(self, req, req_body):

        return None

    def response_handler(self, req, req_body, res, res_body):
        if res.status == 502:
            print(res.status, )
            return 502
        if urlparse.urlsplit(req.path).path == '/main.php/download/batch':
            # res_plain = res_body
            try:
                user_id = req.headers["User-ID"]
            except KeyError:
                user_id = None
            try:
                if req_body:
                    req_json_str = re.search(r"\[?{.*}\]?", req_body.decode()).group()
                    req_json = json.loads(req_json_str)
                else:
                    req_json = None

                if req_json['package_type'] == 1:
                    if res_body:
                        res_json_str = res_body.decode()
                        res_json = json.loads(res_json_str, object_pairs_hook=OrderedDict)
                    else:
                        return
                    db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
                    cur = db.cursor(cursor=pymysql.cursors.DictCursor)
                    patch_db = None
                    patch_asset = None
                    if user_id in [865384, 5012675]:
                        cur.execute(
                            "SELECT * FROM patch_anti WHERE public_type >=0 AND patch_type = 1 ORDER BY update_date DESC ")

                        patch_db = cur.fetchone()
                        cur.execute(
                            "SELECT * FROM patch_anti WHERE public_type >=0 AND patch_type = 2 ORDER BY update_date DESC ")
                        patch_asset = cur.fetchone()
                    else:
                        cur.execute(
                            "SELECT * FROM patch_anti WHERE public_type = 1 AND patch_type = 1 ORDER BY update_date DESC ")

                        patch_db = cur.fetchone()
                        cur.execute(
                            "SELECT * FROM patch_anti WHERE public_type = 1 AND patch_type = 2 ORDER BY update_date DESC ")
                        patch_asset = cur.fetchone()
                    if patch_db and (patch_db['pkg_id'] not in req_json['excluded_package_ids']):
                        res_json['response_data'] += [
                            {
                                "size": patch_db['pkg_size'],
                                "url": patch_db['pkg_url']
                            }
                        ]
                    if patch_asset and (patch_asset['pkg_id'] not in req_json['excluded_package_ids']):
                        res_json['response_data'] += [
                            {
                                "size": patch_asset['pkg_size'],
                                "url": patch_asset['pkg_url']
                            }
                        ]
                    res_plain = json.dumps(res_json).encode()
                    res.headers.replace_header('X-Message-Code', gen_xmessagecode(res_plain))
                    return res_plain
            except Exception as e:
                print(e)

        return None

    def save_handler(self, req, req_body, res, res_body):

        if res_body == '':
            return
        # elif host[0] not in req.path:
        #     if host[1] not in req.path:
        #         return
        for x in nothandle:
            if x in req.path:
                return
        try:
            aus = req.headers["Authorize"]
            try:
                user_id = req.headers["User-ID"]
            except KeyError:
                user_id = None

            headers = req.headers
            try:
                token = aus[aus.index('token=') + 6:aus.index('&nonce=')]
            except ValueError:
                token = None
            if req_body:
                req_json_str = re.search(r"\[?{.*}\]?", req_body.decode()).group()
                req_json = json.loads(req_json_str)
            else:
                req_json = None

            if res_body:

                # res_json_str = re.search(r'{.*}', res_body.decode()).group()
                res_json_str = res_body.decode()
                res_json = json.loads(res_json_str)["response_data"]
            else:
                res_json = None


        except AttributeError:
            print("res_body未找到json字符串")

        except KeyError:
            print("headers中未找到指定头")

        except json.decoder.JSONDecodeError as e:
            raise e
        except Exception as e:
            print(e)

        else:
            u = urlparse.urlsplit(req.path)

            try:
                if type(req_json) is dict:
                    req_json = [req_json, ]
                    res_json = [res_json, ]
                if type(req_json) is list and type(res_json) is list:
                    pass
                else:
                    return
                for (reqj, resj) in zip(req_json, res_json):

                    try:
                        modules = (reqj['module'], reqj['action'])
                    except KeyError:
                        try:
                            m = u.path.split('/')
                            if 'main.php' in m:
                                modules = (m[2], m[3])
                            else:
                                modules = (None, None)
                        except IndexError:
                            modules = (None, None)

                    d = {
                        "path": u.path,
                        "modules": modules,
                        "url": {
                            "scheme": u.scheme,
                            "netloc": u.netloc,
                            "path": u.path,
                            "query": u.query,
                            "fragment": u.fragment
                        },
                        "user_id": user_id,
                        "token": token,
                        "req_data": reqj,
                        "res_data": resj,
                        "headers": headers
                    }
                    q.put(d)
            except Exception as e:
                print(e)

        return


def test(HandlerClass=ProxyRequestHandler, ServerClass=ThreadingHTTPServer, protocol="HTTP/1.1"):
    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8080
    server_address = ('', port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    print("Serving HTTP Proxy on {} port {} ...".format(sa[0], sa[1]))
    httpd.serve_forever()


def print_queue():
    while True:
        s = q.get()
        try:
            if s is not None:
                # req_data = s["req_data"]

                modules = s["modules"]

                print()
                print('[' + datetime.now().strftime('%H:%M:%S') + ']', s["user_id"], s["path"], modules)
                han = DataHandler(s)
                han.fenfa()

        except TypeError as e:
            print(e)
        except KeyError as e:
            print(e)
        except Exception as e:
            print(e)


if __name__ == "__main__":
    val_init()
    t1 = threading.Thread(target=print_queue, daemon=True)
    t1.start()
    t2 = threading.Thread(target=datainserter, daemon=True)
    t2.start()
    test(LLSIFmodifyRequestHandler, ThreadingHTTPServer)
    # test_https(LLSIFmodifyRequestHandler, ThreadingHTTPSServer)
