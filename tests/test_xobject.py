import re

import pytest

from xpattern import MatchError
from xpattern import X
from xpattern import _
from xpattern import caseof
from xpattern import m
from xpattern import xfunction


class Item(object):
    a = 1


# fmt: off
@pytest.mark.parametrize(
    "x_expression, argument, expected",
    [
        (+X, 1, 1),
        (+X, -1, -1),
        (-X, 1, -1),
        (-X, -1, 1),
        (~X, 1, -2),
        (X + 1, 1, 2),
        (X - 1, 3, 2),
        (X * 2, 3, 6),
        (X / 2, 1, 0.5),
        (X // 2, 1, 0),
        (X % 2, 3, 1),
        (X ** 2, 3, 9),
        (X << 2, 3, 12),
        (X >> 2, 9, 2),
        (X & 0x101, 0x111, 257),
        (X | 0x101, 0x111, 273),
        (X ^ 0x101, 0x111, 16),
        (X < 12, 1, True),
        (X < 12, 12, False),
        (X < 12, 13, False),
        (X <= 12, 1, True),
        (X <= 12, 12, True),
        (X <= 12, 13, False),
        (X > 12, 1, False),
        (X > 12, 12, False),
        (X > 12, 13, True),
        (X >= 12, 1, False),
        (X >= 12, 12, True),
        (X >= 12, 13, True),
        (X == 12, 12, True),
        (X == 12, 11, False),
        (X != 12, 12, False),
        (X != 12, 11, True),
        (1 + X, 1, 2),
        (3 - X, 1, 2),
        (2 * X, 3, 6),
        (1 / X, 2, 0.5),
        (1 // X, 2, 0),
        (3 % X, 2, 1),
        (2 ** X, 3, 8),
        (3 << X, 2, 12),
        (9 >> X, 2, 2),
        (0x111 & X, 0x101, 257),
        (0x111 | X, 0x101, 273),
        (0x111 ^ X, 0x101, 16),
        (1 < X, 12, True),
        (12 < X, 12, False),
        (13 < X, 12, False),
        (1 <= X, 12, True),
        (12 <= X, 12, True),
        (13 <= X, 12, False),
        (1 > X, 12, False),
        (12 > X, 12, False),
        (13 > X, 12, True),
        (1 >= X, 12, False),
        (12 >= X, 12, True),
        (13 >= X, 12, True),
        (12 == X, 12, True),
        (13 == X, 12, False),
        (12 != X, 12, False),
        (13 != X, 12, True),
        (X.a, Item(), 1),
        (X[2], [12, 34, 56], 56),
        (X[1][2], [[1, 2], [3, 4, 5]], 5),
        (X["a"], {"a": "apple", "b": "orange"}, "apple"),
        (X[1:3], [1, 4, 5, 9], [4, 5]),
        (X + [3, 4], [1, 2], [1, 2, 3, 4]),
        (X._in_(["a", "b"]), "a", True),
        (X._in_(["a", "b"]), "c", False),
        (X._contains_("a"), ["a", "b"], True),
        (X._contains_("c"), ["a", "b"], False),
        (X._is_(None), None, True),
        (X._is_(None), False, False),
        (X._not(), False, True),
        (X._not(), True, False),
        (X._not(), [], True),
        (X(1, 2, 4), lambda x, y, z: x * y * z, 8),
        (X + X, 7, 14),
        (X ** 2 - 3 + X, 6, 39),
        (X ** (2 - 3 + X), 6, 7776),
    ],
)
def test_operators(x_expression, argument, expected):
    assert x_expression._x_func(argument) == expected


@pytest.mark.parametrize(
    "case, expected",
    [
        (caseof(1) | m(1) >> X + 1, 2),
        (caseof([1, 2, 3]) | m([1, _, 3]) >> X + 1, 3),
        (caseof([1, 2, 3]) | m([1, _, 3]) >> (X ** (3 * 2 - X)), 16),
        (caseof(Item()) | m(Item) >> X.a, 1),
        (caseof({"a": 1, "b": 2}) | m(dict) >> X["b"], 2),
        (caseof("fuffy-my-dog") | m(re.compile(r"(\w+)-(\w+)-dog")) >> X[0], "fuffy"),
        (caseof("fuffy-my-dog") | m(re.compile(r"(\w+)-(\w+)-dog")) >> X[0].upper(), "FUFFY"),
        (caseof("fuffy-my-dog") | m(re.compile(r"\w+-\w+-dog")) >> X.upper(), "FUFFY-MY-DOG"),
    ],
)
def test_action_with_xobject(case, expected):
    assert ~case == expected


def test_chain_caseof():
    assert ~(caseof([1, 2, 3])
        | m(_, _, 3) >> ~(caseof(X) | m(_, 2) >> X)
    ) == 1

    pet = {"type": "dog", "details": {"age": 3}}
    assert ~(caseof(pet)
        | m({_: {"age": _}}) >> ~(caseof(X)
            | m(int, int) >> (lambda x, y: x + y)
            | m(str, int) >> (lambda x, y: y))
    ) == 3


def test_dataclasses_with_chain_caseof():
    try:
        from dataclasses import dataclass
    except ImportError:
        return

    @dataclass
    class Class1:
        a: int
        b: int

    @dataclass
    class Class2:
        data: Class1

    obj = Class2(Class1(a=1, b=2))

    assert ~(caseof(obj)
        | m(Class2(_)) >> ~(
            caseof(X) | m(Class1(_, _)) >> (lambda a, b: (a, b)))
    )  == (1, 2)  # noqa


def test_match_XObject():
    assert ~(caseof((1, 2, 3))
        | m(X[2] == 3) >> True
    )

    with pytest.raises(MatchError):
        ~(caseof((1, 2, 3))
            | m(X[2]) >> True
        )

    assert ~(caseof("abc")
        | m(X.upper() == "ABC") >> True
        | _ >> False
    )

    assert ~(caseof((1, 2, 3))
        | m(X[2] == 3) >> X[2] + 4
    ) == 7

    assert ~(caseof(9)
        | m(X ** 2 - X + 2 == 74) >> True
        | _ >> False
    )


def test_match_XObject_with_getitem_style():
    assert ~(caseof((1, 2, 3))
        | m[X[2] == 3] >> True
    )

    with pytest.raises(MatchError):
        ~(caseof((1, 2, 3))
            | m[X[2]] >> True
        )

    assert ~(caseof("abc")
        | m[X.upper() == "ABC"] >> True
        | _ >> False
    )

    assert ~(caseof((1, 2, 3))
        | m[X[2] == 3] >> X[2] + 4
    ) == 7

    assert ~(caseof(9)
        | m[X ** 2 - X + 2 == 74] >> True
        | _ >> False
    )


def test_xfunction():
    @xfunction
    def add(a, b):
        return a + b

    assert add(X, X + 1)._x_func(1) == 3
    assert add(X, b=X + 1)._x_func(1) == 3
    assert add(a=X, b=X + 1)._x_func(1) == 3
    assert add(a=add(X + 1, 4), b=add(X * 9, 7))._x_func(2) == 32


def test_xfunction_action():
    @xfunction
    def add(a, b):
        return a + b

    assert ~(caseof([1, "b", 2])
        | m(_, "b", _) >> add(X[0], X[1] + 1)
    ) == 4


def test_xfunction_pattern():
    @xfunction
    def greater_than_4(x):
        return x > 4

    assert ~(caseof(1)
        | m(greater_than_4(X + 5)) >> "greater than 4"
        | _ >> "equal or lesser than 4"
    ) == "greater than 4"

    assert ~(caseof(1)
        | m(greater_than_4(X)) >> "greater than 4"
        | _ >> "equal or lesser than 4"
    ) == "equal or lesser than 4"
