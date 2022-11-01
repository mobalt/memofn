import pytest

from momoize.mvp import memofn


def string_appender():
    s = ""

    def internal_concat(*args, **kwargs):
        nonlocal s
        s += "".join(args) + "".join(kwargs.values())
        return s

    return internal_concat


class Foo:
    def __init__(self, x):
        self.x = x

    def bar(self, y):
        self.x += y
        return self.x

    @memofn(ignore_first_n_args=0)
    def mbar(self, y):
        self.x += y
        return self.x

    def __repr__(self):
        return f"Foo{self.x}"


def test_basic_concat():
    cc = string_appender()
    assert cc("a") == "a", "Should concat whatever params it has been fed"
    assert (
        cc("b", "c", d="d", e="e") == "abcde"
    ), "Should concat additional params to original params"
    assert cc("b", "c", e="e", d="d") == "abcdebced", "Should take key pairs in order"


def test_memoize_concat():
    """
    Synonymous with using `@memofn` above `def concat()`
    """
    cc = memofn(string_appender())
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
    cc = memofn(expire_in_days=9)(string_appender())
    assert cc("a") == "a"
    assert cc("a") == "a"


def test_memofn_namespaces():
    a1 = memofn(string_appender(), ns="a")
    a2 = memofn(string_appender(), ns="a")
    b1 = memofn(string_appender(), ns="b")

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
    a = memofn(string_appender())
    b = memofn(string_appender())

    assert a("x") == "x"
    assert a("x") == "x"
    assert a("y") == "xy"
    assert a("z") == "xyz"
    assert b("z") == "xyz"
    assert b("y") == "xy"
    assert b("x") == "x"


def test_memofn_with_classes():
    f = Foo(1)
    g = Foo(1)
    f.bar = memofn(f.bar)
    assert f.bar(2) == 3
    assert f.bar(2) == 3
    assert f.mbar(2) == 5
    assert f.mbar(2) == 7

    assert g.bar(100) == 101
    assert g.mbar(2) == 103
    assert g.mbar(2) == 103
    assert g.bar(2) == 7
