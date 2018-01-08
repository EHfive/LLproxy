#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from collections import OrderedDict
from datetime import datetime
from proxy2.proxy2 import *
from proxy2.https_trasparent import ThreadingHTTPSServer
from proxy2.https_trasparent import test as test_https
from LLConnectionDataHandler import *
# from ReqDataHandler import *
import queue
import threading
import urllib.parse as urlparse
import json
from gen_xmessagecode import gen_xmessagecode
import config as cfg
from mysql import Mysql
import requests as rq


REQ_PATTERN = re.compile(r"\[?{.*}\]?")
host_white_list = ['prod.game1.ll.sdo.com', 'mgame.sdo.com', 'mygm.sdo.com', 'woa.sdo.com']
nothandle = ['/webview.php', '/main.php/resources', '/main.php/eventscenario',
             '/main.php/personalnotice', '/main.php/tos', '/main.php/subscenario', '/main.php/secretbox/all']
nothandle_api = ['rewardList', ]
q = queue.Queue()

pkg_times = {}
name_dict = json.load(open('data/name_zh_jp.json'))['key_name']
my = Mysql(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME)


class LLSIFmodifyRequestHandler(ProxyRequestHandler):
    # def request_handler(self, req, req_body):
    #     netloc = urlparse.urlsplit(req.path).netloc
    #     if netloc not in host_white_list:
    #         return False
    #
    #     try:
    #         user_id = req.headers["User-ID"]
    #         user_id = user_id and int(user_id)
    #     except KeyError:
    #         user_id = None
    #     if user_id not in reqHandle_userList:
    #         return
    #     if req_body is None:
    #         return
    #     reqh = ReqHandler(req, req_body)
    #     req, req_body = reqh.start()
    #     return req_body

    # def response_handler(self, req, req_body, res, res_body):
    #     if res.status == 502:
    #         print(res.status, )
    #         return 502
    #     req_path = urlparse.urlsplit(req.path).path
    #     if req_path == '/main.php/notice/noticeFriendVariety':
    #         try:
    #             user_id = int(req.headers["User-ID"])
    #         except Exception:
    #             return
    #         if res_body:
    #             res_json_str = res_body.decode()
    #             res_json = json.loads(res_json_str, object_pairs_hook=OrderedDict)
    #         else:
    #             return
    #         # print(res_json)
    #
    #         db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
    #         cur = db.cursor()
    #         cur.execute("select rplc_stat from users WHERE uid = {}".format(user_id))
    #         resu = cur.fetchone()
    #         if resu[0] == 0:
    #             return
    #         print("not returned")
    #         for key, val in enumerate(res_json['response_data']['notice_list']):
    #             if val['notice_template_id'] in (14, 15, 16):
    #                 msg = val['message']
    #                 try:
    #                     a = msg.index('「')
    #                     b = msg.index('」')
    #                     title = msg[a + 1:b].split(']')
    #                     if len(title) == 2:
    #                         prefix = title[0] + ']'
    #                         title = title[1]
    #                     else:
    #                         title = title[0]
    #                         prefix = ''
    #                     jp_name = name_dict[title][0]
    #                 except (KeyError, IndexError) as e:
    #                     print(e)
    #                     continue
    #                 else:
    #                     newmsg = msg[0:a + 1] + prefix + jp_name + msg[b:]
    #                     if val['notice_template_id'] == 15:
    #                         newmsg = newmsg.replace('全连击', 'FULL COMBO')
    #
    #                     res_json['response_data']['notice_list'][key]['message'] = newmsg
    #         res_plain = json.dumps(res_json).encode()
    #         res.headers.replace_header('X-Message-Code', gen_xmessagecode(res_plain))
    #         return res_plain
    #     elif req_path == '/main.php/download/batch':
    #         # res_plain = res_body
    #         try:
    #             user_id = int(req.headers["User-ID"])
    #         except KeyError:
    #             user_id = None
    #
    #         try:
    #             if req_body:
    #                 req_p = REQ_PATTERN
    #                 req_json_str = req_p.search(req_body.decode()).group()
    #                 req_json = json.loads(req_json_str)
    #             else:
    #                 req_json = None
    #             if req_json['package_type'] == 4:
    #                 return
    #             elif req_json['package_type'] == 1:
    #                 force_down = False
    #                 if res_body:
    #                     res_json_str = res_body.decode()
    #                     res_json = json.loads(res_json_str, object_pairs_hook=OrderedDict)
    #                 else:
    #                     return
    #                 try:
    #                     times = pkg_times[user_id]
    #                 except KeyError:
    #                     pkg_times[user_id] = [1, int(time.time())]
    #                     return
    #                 else:
    #                     if int(time.time()) - pkg_times[user_id][1] <= 15:
    #                         pkg_times[user_id][0] += 1
    #                     else:
    #                         pkg_times[user_id] = [1, int(time.time())]
    #
    #                     if pkg_times[user_id][0] >= 3:
    #
    #                         force_down = True
    #                     elif pkg_times[user_id][0] >= 2:
    #
    #                         print("patch", pkg_times[user_id][0], int(time.time()) - pkg_times[user_id][1])
    #                     else:
    #                         return
    #
    #                 db = pymysql.connect(cfg.DB_HOST, cfg.DB_USER, cfg.DB_PASSWORD, cfg.DB_NAME, charset=cfg.DB_CHARSET)
    #                 cur = db.cursor(cursor=pymysql.cursors.DictCursor)
    #                 version = req.headers.get('Client-Version')
    #                 if user_id in [865384, 5012675]:
    #                     pub_type = 0
    #                 else:
    #                     pub_type = 1
    #
    #                 sql = """SELECT s.*
    #                 FROM (SELECT max(update_date) AS update_date FROM `patch_anti` WHERE pkg_version LIKE '{}' AND
    #                 public_type >= '{}' GROUP BY `patch_type` LIMIT 10) t
    #                 LEFT JOIN `patch_anti` AS s ON t.update_date=s.update_date""".format(version, pub_type)
    #                 cur.execute(sql)
    #                 resu = cur.fetchall()
    #                 if not resu:
    #                     return
    #                 for patch in resu:
    #                     if patch and ((patch['pkg_id'] not in req_json['excluded_package_ids']) or force_down):
    #                         try:
    #                             respon = rq.head(patch['pkg_url'])
    #                             if respon.status_code == 404:
    #                                 continue
    #                             pkg_size = int(respon.headers.get("Content-Length"))
    #                         except:
    #                             pkg_size = patch['pkg_size']
    #                         res_json['response_data'] += [
    #                             {
    #                                 "size": pkg_size,
    #                                 "url": patch['pkg_url']
    #                             }
    #                         ]
    #
    #                 if len(res_json['response_data']) > 0 or force_down:
    #                     del pkg_times[user_id]
    #                 res_plain = json.dumps(res_json).encode()
    #                 res.headers.replace_header('X-Message-Code', gen_xmessagecode(res_plain))
    #                 return res_plain
    #         except Exception as e:
    #             print(e)
    #     elif req_path == '/main.php/rlive/lot':
    #         try:
    #             user_id = int(req.headers["User-ID"])
    #         except KeyError:
    #             user_id = None
    #         if user_id in pkg_times:
    #             del pkg_times[user_id]
    #     return None

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
                user_id = user_id and int(user_id)
            except KeyError:
                user_id = None

            headers = req.headers
            try:
                token = aus[aus.index('token=') + 6:aus.index('&nonce=')]
            except ValueError:
                token = None
            if req_body:
                req_p = REQ_PATTERN
                req_json_str = req_p.search(req_body.decode()).group()
                req_json = json.loads(req_json_str)
            else:
                req_json = None

            if res_body:

                # res_json_str = re.search(r'{.*}', res_body.decode()).group()

                res_json_str = utf8decode(res_body)

                res_json = json.loads(res_json_str)["response_data"]
            else:
                res_json = None


        except AttributeError:
            print("res_body未找到json字符串")

        except KeyError:
            print("headers中未找到指定头")

        except json.decoder.JSONDecodeError as e:
            print(e, "JSONDecodeError line232")
            return
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


def utf8decode(s):
    for encoding in "utf-8-sig", "utf-8":
        try:
            return s.decode(encoding)
        except UnicodeDecodeError:
            continue
    return s.decode("latin-1")


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
