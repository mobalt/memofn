import datetime
import functools
import os
import pickle
import types

from memofn.utils.hashable import make_hashable


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
global_cache_path = ".cache"


def always_false(*args, **kwargs):
    return False


def memofn(
    fn=None, expire_in_days=None, ns="", unless_fn=None, ignore_first_n_args=None
):
    # If fn is not provided, then curry the function
    if fn is None:
        return functools.partial(
            memofn, expire_in_days=expire_in_days, ns=ns, unless_fn=unless_fn
        )

    # If first arg is self, then ignore it
    is_method = isinstance(fn, types.MethodType)
    if ignore_first_n_args is None:
        ignore_first_n_args = 1 if is_method else 0

    # If no unless_fn is provided, then use a function that always returns False
    if unless_fn is None:
        unless_fn = always_false

    global global_cache
    if not ns:
        ns = namespace(fn)
    if ns not in global_cache:
        global_cache[ns] = {}
    local_cache = global_cache[ns]

    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        is_method = isinstance(wrapper, types.MethodType)
        key = make_hashable((args[ignore_first_n_args:], kwargs))

        if key in local_cache:
            memo_value = local_cache[key]
            # Should we use cached value? Or recalculate a new one?
            if not unless_fn(*args, **kwargs) or (
                expire_in_days is None or memo_value.created_days_ago <= expire_in_days
            ):
                memo_value.bump()
                return memo_value.value

            # Delete old value
            del local_cache[key]
        # Calculate new value
        value = fn(*args, **kwargs)
        local_cache[key] = MemoValue(value)
        return value

    return wrapper


def load_cache(path: str = None):
    """
    Load the global cache from a pickle file.

    Args:
        path (str, optional): Path to the pickle file. Defaults to ".cache". Path is saved for later save_cache() calls.

    Returns:
        dict: The global cache
    """

    global global_cache, global_cache_path
    if path is None:
        path = global_cache_path
    else:
        global_cache_path = path

    try:
        with open(path, "rb") as f:
            global_cache = pickle.load(f)
    except FileNotFoundError:
        global_cache = {}

    return global_cache


def save_cache(path: str = None):
    """Save the global cache to a pickle file

    Args:
        path (str, optional): Path to the pickle file. Defaults to ".cache".

    """
    global global_cache, global_cache_path

    if not global_cache:
        global_cache = {}

    if path is None:
        path = global_cache_path

    with open(path, "wb") as f:
        pickle.dump(global_cache, f)


def clear_cache():
    """Clear the global cache and remove the cache file"""
    global global_cache, global_cache_path
    global_cache = {}
    os.remove(global_cache_path)
