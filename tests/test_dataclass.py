from xpattern import X
from xpattern import _
from xpattern import caseof
from xpattern import m


# fmt: off
def test_dataclasses():
    try:
        from dataclasses import dataclass
    except ImportError:
        return

    @dataclass
    class Point:
        x: float
        y: float

    def f(x):
        return ~(caseof(x)
            | m(Point(1, 2)) >> "1"
            | m(Point(_, 2)) >> str
            | m(Point(1, _)) >> str
            | m(Point(_, _)) >> (lambda a, b: str(a + b))
        )

    assert f(Point(1, 2)) == "1"
    assert f(Point(2, 2)) == "2"
    assert f(Point(1, 3)) == "3"
    assert f(Point(2, 3)) == "5"


def test_different_dataclasses():
    try:
        from dataclasses import dataclass
    except ImportError:
        return

    @dataclass
    class Cat:
        name: str
        chassed_squirels: int

    @dataclass
    class Dog:
        name: str
        chassed_squirels: int

    def what_is(x):
        return ~(caseof(x)
            | m(Dog(_, 0)) >> "good boy"
            | m(Dog(_, _)) >> "doggy!"
            | m(Cat(_, 0)) >> "tommy?"
            | m(Cat(_, _)) >> "a cat"
        )

    assert what_is(Cat("cat", 0)) == "tommy?"
    assert what_is(Cat("cat", 1)) == "a cat"
    assert what_is(Dog("", 0)) == "good boy"
    assert what_is(Dog("", 1)) == "doggy!"


def test_dataclasses_with_xobject_action():
    try:
        from dataclasses import dataclass
    except ImportError:
        return

    @dataclass
    class Point:
        x: float
        y: float

    def f(x):
        return ~(caseof(x)
            | m(Point(1, 2)) >> X
            | m(Point(_, 2)) >> X + 1
            | m(Point(1, _)) >> X ** 2
            | m(Point(_, _)) >> X * 2
        )

    assert f(Point(1, 2)) == Point(1, 2)
    assert f(Point(3, 2)) == 4
    assert f(Point(1, 9)) == 81
    assert f(Point(7, 3)) == [7, 3, 7, 3]
