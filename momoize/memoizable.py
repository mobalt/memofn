import typing
import copy
import pickle
import time
from pathlib import Path

from momoize.utils.hashable import make_hashable


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
