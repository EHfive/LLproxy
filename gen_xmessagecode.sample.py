'''This is an example of what gen_xmessagecode may look like.

In the actual game client, X-Message-Code is a HMAC-SHA1 of the request body.
The HMAC key can be found by disassemling the NDK binary.'''

import hmac


def gen_xmessagecode(data):
    hmacsha1 = hmac.new(b'', digestmod='sha1')
    hmacsha1.update(data)
    return hmacsha1.hexdigest()
