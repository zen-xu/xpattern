from datetime import datetime
from typing import List
from typing import NewType
from typing import Optional
from typing import Tuple
from typing import Union

import pytest

from xpattern import REST
from xpattern import TAIL
from xpattern import _
from xpattern import caseof
from xpattern import m


# fmt: off


def test_fibonacci():
    def fib(n):
        return ~(caseof(n)
            | m(1) >> 1
            | m(2) >> 1
            | _ >> (lambda x: fib(x - 1) + fib(x - 2))
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
            | m(callable, REST) >> (lambda f, rest: f(*map(lisp, rest)))
            | m(tuple) >> (lambda t: list(map(lisp, t)))
        )

    plus = lambda a, b: a + b
    minus = lambda a, b: a - b
    assert lisp((plus, 1, 2)) == 3
    assert lisp((plus, 1, (minus, 4, 2))) == 3
    assert lisp((reduce, plus, (1, 2, 3))) == 6
    assert lisp((reduce, plus, (range, 10))) == 45


@pytest.mark.parametrize(
    "args, expected",
    [
        (([1, 2, 3], [4, 5, 6]), [(1, 4), (2, 5), (3, 6)]),
        ((range(5), range(5)), list(zip(range(5), range(5)))),
    ]
)
def test_myzip(args, expected):
    def myzip(a, b):
        return ~(caseof((a, b))
            | m(([], [])) >> []
            | m(([_, TAIL], [_, TAIL])) >> (lambda ha, ta, hb, tb: [(ha, hb)] + myzip(ta, tb))
        )

    assert myzip(*args) == expected


def test_lambda_cond():
    cond = lambda x: x < 10
    assert ~(caseof(3)
        | m(cond) >> "action"
        | _ >> "else"
    ) == "action"

    assert ~(caseof(11)
        | m(cond) >> "action1"
        | _ >> "else"
    ) == "else"


def test_lambda_cond_arg_passing():
    def f(x):
        return ~(caseof(x)
            | m(lambda x: x % 2 == 0) >> (lambda x: "even %d" % x)
            | m(lambda x: x % 2 != 0) >> (lambda x: "odd %d" % x)
        )

    assert f(3) == "odd 3"
    assert f(18) == "even 18"


def test_animals():
    pets = [
        {"type": "dog", "pet-details": {"name": "carl", "cuteness": 4}},
        {"type": "dog", "pet-details": {"name": "john", "cuteness": 3}},
        {"type": "cat", "pet-details": {"name": "fuffy", "cuty": 4.6}},
        {"type": "cat", "cat-details": {"name": "bonney", "cuty": 7}},
    ]

    def avg_cuteness_pampy():
        cutenesses = []
        for pet in pets:
            ~(caseof(pet)
                | m({_: {"cuteness": _}}) >> (lambda key, x: cutenesses.append(x))
                | m({_: {"cuty": _}}) >> (lambda key, x: cutenesses.append(x))
            )
        return sum(cutenesses) / len(cutenesses)

    assert avg_cuteness_pampy() == (4 + 3 + 4.6 + 7) / 4


def test_advanced_lambda():
    def either(pattern1, pattern2):
        """Matches values satisfying pattern1 OR pattern2"""

        def repack(*args):
            return True, list(args)

        def f(var):
            return ~(caseof(var)
                | m(pattern1) >> repack
                | m(pattern2) >> repack
                | _ >> (False, [])
            )

        return f

    assert ~(caseof("str")
        | m(either(int, str)) >> "success"
    ) == "success"

    def datetime_p(year: int, month: int, day: int, hour: int = 0, minute: int = 0, second: int = 0):
        """Matches a datetime with these values"""

        def f(var: datetime):
            if not isinstance(var, datetime):
                return False, []

            args = []
            for pattern, actual in [(year, var.year), (month, var.month), (day, var.day),
                                    (hour, var.hour), (minute, var.minute), (second, var.second)]:
                if pattern is _:
                    args.append(actual)
                elif pattern != actual:
                    return False, []

            return True, args

        return f

    def test(var):
        return ~(caseof(var)
            | m(datetime_p(2018, 12, 23)) >> "full match"
            | m(datetime_p(2018, _, _)) >> (lambda month, day: f'{month}/{day} in 2018')
            | m(datetime_p(_, _, _, _, _, _)) >> "any datetime"
            | _ >> "not a datetime"
        )

        assert test(datetime(2018, 12, 23)) == "full match"
        assert test(datetime(2018, 1, 2)) == "1/2 in 2018"
        assert test(datetime(2017, 1, 2, 3, 4, 5)) == "any datetime"
        assert test(11) == "not a datetime"


def test_typing_example():
    timestamp = NewType("timestamp", Union[float, int])
    year, month, day, hour, minute, second = int, int, int, int, int, int
    day_tuple = Tuple[year, month, day]
    dt_tuple = Tuple[year, month, day, hour, minute, second]

    def datetime_p(patterns: List[str]):
        def f(dt: str):
            for pattern in patterns:
                try:
                    return True, [datetime.strptime(dt, pattern)]
                except Exception:
                    continue
            else:
                return False, []
        return f

    def to_datetime(dt: Union[
        timestamp,
        day_tuple,
        dt_tuple,
        str,
    ]) -> Optional[datetime]:
        return ~(caseof(dt)
            | m(timestamp) >> (lambda x: datetime.fromtimestamp(x))
            | m(Union[day_tuple, dt_tuple]) >> (lambda *x: datetime(*x))
            | m(datetime_p(["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"])) >> (lambda x: x)
            | _ >> None
        )

    key_date_tuple = (2018, 1, 1)
    detailed_key_date_tuple = (2018, 1, 1, 12, 5, 6)
    key_date = datetime(*key_date_tuple)
    detailed_key_date = datetime(*detailed_key_date_tuple)

    assert to_datetime(key_date_tuple) == key_date
    assert to_datetime(detailed_key_date_tuple) == detailed_key_date

    key_date_ts = key_date.timestamp()
    detailed_key_date_ts = int(detailed_key_date.timestamp())
    assert to_datetime(key_date_ts) == key_date
    assert to_datetime(detailed_key_date_ts) == detailed_key_date

    key_date_ts_str_a = key_date.strftime("%Y-%m-%d")
    key_date_ts_str_f = key_date.strftime("%Y-%m-%d %H:%M:%S")
    key_date_ts_str_w = key_date.strftime("%m-%Y-%d")

    assert to_datetime(key_date_ts_str_a) == key_date
    assert to_datetime(key_date_ts_str_f) == key_date
    assert to_datetime(key_date_ts_str_w) is None

    detailed_key_date_ts_str = detailed_key_date.strftime("%Y-%m-%d %H:%M:%S")
    assert to_datetime(detailed_key_date_ts_str) == detailed_key_date
    assert to_datetime(set(key_date_tuple)) is None
