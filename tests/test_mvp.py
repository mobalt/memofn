import pytest

from momoize.mvp import memofn


def concat():
    s = ""

    def internal_concat(*args, **kwargs):
        nonlocal s
        s += "".join(args) + "".join(kwargs.values())
        return s

    return internal_concat


def test_basic_concat():
    cc = concat()
    assert cc("a") == "a"
    assert cc("b", "c", d="d", e="e") == "abcde"
    assert cc("b", "c", e="e", d="d") == "abcdebced"


def test_memoize_concat():
    """
    Synonymous with using `@memofn` above `def concat()`
    """
    cc = memofn(concat())
    assert cc("a") == "a"
    assert cc("b", "c", d="d", e="e") == "abcde"
    assert (
        cc("b", "c", e="e", d="d") == "abcde"
    ), "order of kwargs should not matter, since values are same"
    assert (
        cc("b", "c", e="d", d="e") == "abcdebcde"
    ), "key-value pairs are different, so should be different"
    assert (
        cc("b", "c", d="d", e="e") == "abcde"
    ), "old value should be returned, since memoized"


def test_memoize_params_concat():
    """
    Synonymous with using @memofn(expire_in_days=9) above `def concat()`
    :return:
    """
    cc = memofn(expire_in_days=9)(concat())
    assert cc("a") == "a"
    assert cc("a") == "a"


def test_memofn_namespaces():
    a1 = memofn(concat(), ns="a")
    a2 = memofn(concat(), ns="a")
    b1 = memofn(concat(), ns="b")

    assert a1("a") == "a"
    assert a1("a") == "a"
    assert a1("b") == "ab"
    # since a2 has empty string, you might think it would be "b",
    # but actually since it shares namespace with a1, it will be "ab"
    assert a2("b") == "ab"
    # This doesn't share namespace, so it will be "b"
    assert b1("b") == "b"
    assert a2("c") == "c"
    assert a1("c") == "c"
    assert b1("c") == "bc"


def test_memofn_namespaces_in_pytest():
    a = memofn(concat())
    b = memofn(concat())

    assert a("x") == "x"
    assert a("x") == "x"
    assert a("y") == "xy"
    assert a("z") == "xyz"
    assert b("x") == "x"
    assert b("z") == "xyz"
