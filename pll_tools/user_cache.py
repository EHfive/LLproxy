users = {}


def _get_user(uid):
    try:
        return users[uid]
    except KeyError:
        pass

    return {}


def get_bykey(uid, key, default=0):
    try:
        return _get_user(uid)[key]
    except KeyError:
        pass

    return default


def set_kv(uid, key, value):
    users[uid] = _get_user(uid)
    users[uid][key] = value
