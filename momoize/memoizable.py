import typing
from collections.abc import Iterable
import copy
import pickle
import time
from pathlib import Path


def is_hashable(item: typing.Any) -> bool:
    """Try hashing the item. If it fails, it's not hashable.
    Args:
        item: The item to be hashed

    Returns:
        bool: True if the item can be hashed, False otherwise
    """
    try:
        hash(item)
    except TypeError:
        return False
    return True


def is_iterable(item):
    return isinstance(item, Iterable)


def sorted_tuple(item: typing.Any) -> typing.Any:
    """Try sorting the item. If it fails, return the item.
    Args:
        item: The item to be sorted

    Returns:
        item: The sorted item as a tuple, or the original item if it can't be sorted
    """
    try:
        return tuple(sorted(item))
    except TypeError:
        return item


def dict_to_hashable(dict_item: typing.Dict) -> typing.Tuple:
    """Convert a dict into a hashable sorted tuple.
    Args:
        dict_item: The dict to be converted

    Returns:
        tuple: The sorted tuple
    """
    return sorted_tuple(
        ((key, make_hashable(value)) for key, value in dict_item.items())
    )


def iterable_to_hashable(iterable):
    """Convert an iterable into a hashable tuple.
    Args:
        iterable: The iterable to be converted

    Returns:
        tuple: The hashable (sorted tuple)
    """
    return sorted_tuple((make_hashable(item) for item in iterable))


def make_hashable(item: typing.Any) -> typing.Any:
    """Convert an item into a hashable item.

    Args:
        item: The item to be converted

    Returns:
        item: The hashable item
    """
    if is_hashable(item):
        return item
    elif type(item) is dict:
        return dict_to_hashable(item)
    elif is_iterable(item):
        return iterable_to_hashable(item)
    else:
        raise Exception("Can't make hashable: ", item)


def __not_equal__(a, b):
    return a != b


class Memoizable:
    def __init__(
        self,
        cache_file: typing.Union[str, Path] = ".cache",
        expire_in_days=7,
        hashfunc=None,
    ):
        self.__cache__file__ = Path(cache_file)
        self.cache = {}
        self.__expire_in__ = expire_in_days * 60 * 60 * 24
        if hashfunc is not None:
            self.__current_stamp__ = hashfunc
            self.__expiration_stamp__ = None
            self.__is_expired__ = __not_equal__
        self.load_cache()

    def __call__(self, *args, **kwargs):
        hashedargs = self.__preprocess_args__(*args, **kwargs)
        cached = self.cache.get(hashedargs, None)
        current = self.__current_stamp__(*args, **kwargs)
        if cached is None or self.__is_expired__(cached[1], current):
            value = self.run(*args, **kwargs)
            if self.__expiration_stamp__ is not None:
                current = self.__expiration_stamp__(*args, **kwargs)
            self.cache[hashedargs] = value, current
            self.save_cache()
            return copy.deepcopy(value)
        else:
            return copy.deepcopy(self.cache[hashedargs][0])

    def __preprocess_args__(self, *args, **kwargs):
        return make_hashable((*args, kwargs))

    def load_cache(self):
        if self.__cache__file__.exists():
            self.cache = pickle.loads(self.__cache__file__.read_bytes())
        else:
            self.cache = {}

    def save_cache(self, cache_file: typing.Union[Path, None] = None):
        if type(cache_file) is None:
            cache_file = self.__cache__file__
        cache_file.write_bytes(pickle.dumps(self.cache))

    def run(self, *args, **kwargs):
        raise NotImplementedError("Please override the run function.")

    def __is_expired__(self, cached, current):
        return current > cached

    def __current_stamp__(self, *args, **kwargs):
        return time.time() - self.__expire_in__

    def __expiration_stamp__(self, *args, **kwargs):
        return time.time()

    def __repr__(self):
        """Return base execute function's docstring."""
        return self.run.__doc__
