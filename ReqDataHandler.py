import json
import urllib.parse as urlparse
import re
from collections import OrderedDict

from gen_xmessagecode import gen_xmessagecode

reqHandle_userList = []
REQ_PATTERN = re.compile(r"\[?{.*}\]?")


class ReqHandler:
    def __init__(self, req, req_body):
        self._req = req
        self._req_body = req_body
        req = self._req
        req_body = self._req_body
        self.req_p = REQ_PATTERN
        self.url = urlparse.urlsplit(req.path)
        try:
            try:
                user_id = req.headers["User-ID"]
                user_id = user_id and int(user_id)
            except KeyError:
                user_id = None

            if req_body:
                req_json_str = self.req_p.search(req_body.decode()).group()
                req_json = json.loads(req_json_str, object_pairs_hook=OrderedDict)
            else:
                req_json = None


        except KeyError:
            print("headers中未找到所需头信息")
            return
        except json.decoder.JSONDecodeError as e:
            print(e, "JSONDecodeError ReqHandler")
            return
        except Exception as e:
            print(e, "ReqHandler unexpected error")
            return

        else:

            self.uid = user_id
            self.req_data = req_json

    def start(self):
        self.fenfa_handler()
        req_json_str = json.dumps(self.req_data, separators=(',', ':'), ensure_ascii=False)
        req_plain = self.req_p.sub(req_json_str, self._req_body.decode()).encode()
        self._req.headers.replace_header('X-Message-Code', gen_xmessagecode(req_json_str.encode()))
        return self._req, req_plain

    def fenfa_handler(self):
        path = self.url.path
        if 'battle/liveEnd' in path:
            count_sc = {}
            muti_default = 1.08
            muti = 1.1
            # muti = input("SCORE MUTI [{}]".format(muti_default))
            if muti:
                muti = float(muti)
            else:
                muti = muti_default
            for k, v in self.req_data.items():
                if 'score_' in k:
                    self.req_data[k] = int(v * muti)
                    count_sc[k] = self.req_data[k]
            print(count_sc)
