import re

from enum import Enum

import pytest

from pampy.helpers import UnderscoreType
from xpattern import HEAD
from xpattern import TAIL
from xpattern import MatchError
from xpattern import _
from xpattern import caseof
from xpattern import m


def test_UnderscoreType_equals():
    assert _ == UnderscoreType()


# fmt: off
@pytest.mark.parametrize(
    "case",
    [
        (caseof(3) | m(3) >> True),
        (caseof(3) | m[3] >> True),
        (caseof(3) | _ >> True),
        (caseof(3)
            | m(1) >> False
            | m(2) >> False
            | m(3) >> True
        ),
        (caseof(3)
            | m[1] >> False
            | m[2] >> False
            | m[3] >> True
        ),
        (caseof([1, 2])
            | m([1]) >> False
            | m([1, 2]) >> True
        ),
        (caseof([1, 2])
            | m[[1]] >> False
            | m[[1, 2]] >> True
        ),
    ]
)
def test_basic(case):
    assert ~case


@pytest.mark.parametrize(
    "case",
    [
        (caseof(3) | m[3] >> True),
        (caseof(3)
            | m[1] >> False
            | m[2] >> False
            | m[3] >> True
        ),
        (caseof([1, 2])
            | m[[1]] >> False
            | m[[1, 2]] >> True
        ),
    ]
)
def test_getitem_style(case):
    assert ~case


def test_match_None():
    assert ~(caseof(None)
        | m(None) >> "None"
        | _ >> 'else') == "None"


def test_match_value_is_vs_equal():
    a = "x" * 1000000
    b = "x" * 1000000
    assert a == b
    assert not (a is b)
    assert ~(caseof(a) | m(b) >> True)


@pytest.mark.parametrize(
    "array, length",
    [
        ([], 0),
        ([1], 1),
        ([1, 2, 3], 3),
    ]
)
def test_match_len(array, length):
    def _len(_array):
        return ~(caseof(_array)
            | m([]) >> 0
            | m([HEAD, TAIL]) >> (lambda head, tail: 1 + _len(tail))
        )

    assert _len(array) == length


def test_match_strict_raises():
    with pytest.raises(MatchError):
        ~(caseof(3) | m(2) >> True)


def test_match_not_strict_returns_false():
    assert not ~(caseof(3, strict=False) | m(2) >> True)


def test_match_default():
    assert not ~(caseof(3, default=False) | m(2) >> True)
    assert ~(caseof(3, default=6) | m(2) >> True) == 6


@pytest.mark.parametrize(
    "case, retrun_value",
    [
        (caseof([1, 2, 3]) | m([1, _, 3]) >> (lambda x: x), 2),
        (caseof([1, 2, 3]) | m([1, 2, 3]) >> (lambda x: x), [1, 2, 3])
    ]
)
def test_match_arguments_passing(case, retrun_value):
    assert ~case == retrun_value


def test_match_action_can_be_empty_list():
    assert ~(caseof(True) | m(True) >> []) == []


def test_match_raise_lambda_error():
    with pytest.raises(MatchError) as error:
        ~(caseof([1, 2, 3])
            | m([1, _, 3]) >> (lambda: "xxxxx {}".format()) # noqa
        )

    assert "lambda" in str(error.value)
    assert "xxxxx" in str(error.value)


def test_match_class_hierarchy():
    class Pet: pass          # noqa
    class Dog(Pet): pass     # noqa
    class Cat(Pet): pass     # noqa
    class Hamster(Pet): pass # noqa

    def what_is(x):
        return ~(caseof(x)
            | m(Dog) >> 'dog'
            | m(Cat) >> 'cat'
            | m(Pet) >> 'any other pet'
            | _ >> 'this is not a pet at all'
        )

    assert what_is(Cat()) == 'cat'
    assert what_is(Dog()) == 'dog'
    assert what_is(Hamster()) == 'any other pet'
    assert what_is(Pet()) == 'any other pet'
    assert what_is(True) == 'this is not a pet at all'


def test_regex_groups():
    def what_is(pet):
        return ~(caseof(pet)
            | m(re.compile(r"(\w+)-(\w+)-cat$")) >> (lambda name, my: "cat " + name)
            | m(re.compile(r"(\w+)-(\w+)-dog$")) >> (lambda name, my: "dog " + name)
            | _ >> "something else"
        )

    assert what_is("fuffy-my-dog") == "dog fuffy"
    assert what_is("puffy-her-dog") == "dog puffy"
    assert what_is("carla-your-cat") == "cat carla"
    assert what_is("roger-my-hamster") == "something else"


def test_regex_no_groups():
    def what_is(pet):
        return ~(caseof(pet)
            | m(re.compile(r"fuffy-cat$")) >> (lambda x: "fuffy-cat")
            | _ >> "something else"
        )

    assert what_is("my-fuffy-cat") == "fuffy-cat"


def test_match_enum():
    class Color(Enum):
        RED = 1
        GREEN = 2
        BLUE = 3

    assert ~(caseof(Color.RED)
        | m(Color.BLUE) >> "blue"
        | m(Color.RED) >> "red"
        | _ >> "else"
    ) == "red"

    assert ~(caseof(Color.RED)
        | m(Color.BLUE) >> "blue"
        | m(Color.GREEN) >> "green"
        | _ >> "else"
    ) == "else"

    assert ~(caseof(1)
        | m(Color.BLUE) >> "blue"
        | m(Color.RED) >> "red"
        | _ >> "else"
    ) == "else"


def test_external_patterns():
    def f(l):
        return ~(caseof(l)
            | m(int, int) >> "[int, int]"
            | m(int, str) >> "[int, str]"
            | m(int, [int, str], int) >> "[int, [int, str], int]"
            | _ >> "other"
        )

    assert f([1, 1]) == "[int, int]"
    assert f([1, "1"]) == "[int, str]"
    assert f([1, [1, "a"], 2]) == "[int, [int, str], int]"
    assert f([1, [1, "a", "c"], 2]) == "other"
    assert f(1) == "other"
