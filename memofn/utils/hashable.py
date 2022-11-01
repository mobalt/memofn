import typing
from typing import Iterable


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
    return tuple((make_hashable(item) for item in iterable))


def make_hashable(item: typing.Any) -> typing.Any:
    """Convert an item into a hashable item.

    Args:
        item: The item to be converted

    Returns:
        item: The hashable item
    """
    if is_hashable(item):
        return repr(item)
    elif type(item) is dict:
        return dict_to_hashable(item)
    elif is_iterable(item):
        return iterable_to_hashable(item)
    else:
        raise Exception("Can't make hashable: ", item)
