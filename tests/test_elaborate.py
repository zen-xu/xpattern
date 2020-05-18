import pytest

from xpattern import REST
from xpattern import X
from xpattern import _
from xpattern import caseof
from xpattern import m


# fmt: off
def test_fibonacci():
    def fib(n):
        return ~(caseof(n)
            | m(1) >> 1
            | m(2) >> 1
            | m(_) >> (lambda x: fib(x - 1) + fib(x - 2))
        )

    assert fib(1) == 1
    assert fib(7) == 13


def test_slide1():
    _input = [1, 2, 3]
    pattern = [1, _, 3]
    action = lambda x: "it's {}".format(x)
    assert ~(caseof(_input) | m(pattern) >> action) == "it's 2"


@pytest.mark.parametrize(
    "exp, expected",
    [
        (3, "the integer 3"),
        (5, "any integer"),
        ("ciao", "the string ciao"),
        ("x", "any string"),
        ({"a": 1}, "any dictionary"),
        ([1], "the list [1]"),
        ([1, 2, 3], "the list [1, 2, 3]"),
        ([1, 2, 4], "the list [1, 2, _]"),
        ([1, 3, 3], "the list [1, _, 3]"),
        (["hello", "world"], "hello world"),
        ([1, [2, 3], 4], "[1, [2, 3], 4]"),
    ]
)
def test_parse(exp, expected):
    def parser(exp):
        return ~(caseof(exp)
            | m(3) >> "the integer 3"
            | m(float) >> "any float number"
            | m(int) >> "any integer"
            | m("ciao") >> "the string ciao"
            | m(dict) >> "any dictionary"
            | m(str) >> "any string"
            | m((int, int)) >> "a tuple made of two ints"
            | m([1]) >> "the list [1]"
            | m([1, 2, 3]) >> "the list [1, 2, 3]"
            | m([1, _, 3]) >> "the list [1, _, 3]"
            | m((str, str)) >> (lambda a, b: "%s %s" % (a, b))
            | m([1, 2, _]) >> (lambda x: "the list [1, 2, _]")
            | m([1, 2, 4]) >> "the list [1, 2, 4]"  # this can never be matched
            | m([1, [2, _], _]) >> (lambda a, b: "[1, [2, %s], %s]" % (a, b))
        )
    assert parser(exp) == expected


def test_lisp():
    from functools import reduce

    def lisp(exp):
        return ~(caseof(exp)
            | m(int) >> (lambda x: x)
            | m(callable) >> (lambda x: x)
            | m((callable, REST)) >> (lambda f, rest: f(*map(lisp, rest)))
            | m(tuple) >> (lambda t: list(map(lisp, t)))
        )

    plus = lambda a, b: a + b
    minus = lambda a, b: a - b
    assert lisp((plus, 1, 2)) == 3
    assert lisp((plus, 1, (minus, 4, 2))) == 3
    assert lisp((reduce, plus, (1, 2, 3))) == 6
    assert lisp((reduce, plus, (range, 10))) == 45
