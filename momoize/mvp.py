import datetime
import functools

from momoize.utils.hashable import make_hashable


class MemoValue:
    def __init__(self, value):
        self.created = datetime.datetime.now()
        self.lastaccessed = datetime.datetime.now()
        self.value = value

    def bump(self):
        self.lastaccessed = datetime.datetime.now()

    @property
    def created_days_ago(self):
        return (datetime.datetime.now() - self.created).days

    @property
    def used_days_ago(self):
        return (datetime.datetime.now() - self.lastaccessed).days


def namespace(fn):
    ns = [
        getattr(fn, "__module__", "<UNKNOWN_MODULE>"),
        getattr(fn, "__qualname__", "<UNKNOWN_QUALNAME>"),
    ]
    # ns += [repr(fn)]
    return ".".join(ns)


global_cache = {}


def memofn(fn=None, expire_in_days=None, ns=""):
    if fn is None:
        return functools.partial(memofn, expire_in_days=expire_in_days, ns=ns)

    global global_cache
    if not ns:
        ns = namespace(fn)
    if ns not in global_cache:
        global_cache[ns] = {}
    local_cache = global_cache[ns]

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = make_hashable((args, kwargs))

        if key in local_cache:
            val = local_cache[key]
            val.bump()
            return val.value
        else:
            val = fn(*args, **kwargs)
            local_cache[key] = MemoValue(val)
            return val

    return wrapper
