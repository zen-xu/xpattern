from collections.abc import Iterable

from pampy import match
from pampy import match_value
from pampy.helpers import BoxedArgs
from pampy.pampy import NoDefault
from pipetools.main import XObject


# Inject external magic methods to XObject
XObject.__lshift__ = lambda self, other: self.bind(
    lambda: "X << {0!r}".format(other), lambda x: x << other
)
XObject.__rshift__ = lambda self, other: self.bind(
    lambda: "X >> {0!r}".format(other), lambda x: x >> other
)
XObject.__radd__ = lambda self, other: self.bind(
    lambda: "{0!r} + X".format(other), lambda x: other + x
)
XObject.__rsub__ = lambda self, other: self.bind(
    lambda: "{0!r} - X".format(other), lambda x: other - x
)
XObject.__rmul__ = lambda self, other: self.bind(
    lambda: "{0!r} * X".format(other), lambda x: other * x
)
XObject.__rdiv__ = lambda self, other: self.bind(
    lambda: "{0!r} / X".format(other), lambda x: other / x
)
XObject.__rfloordiv__ = lambda self, other: self.bind(
    lambda: "{0!r} / X".format(other), lambda x: other // x
)
XObject.__rmod__ = lambda self, other: self.bind(
    lambda: "{0!r} % X".format(other), lambda x: other % x
)
XObject.__rgt__ = lambda self, other: self.bind(
    lambda: "{0!r} > X".format(other), lambda x: other > x
)
XObject.__rge__ = lambda self, other: self.bind(
    lambda: "{0!r} >= X".format(other), lambda x: other >= x
)
XObject.__rlt__ = lambda self, other: self.bind(
    lambda: "{0!r} < X".format(other), lambda x: other < x
)
XObject.__rle__ = lambda self, other: self.bind(
    lambda: "{0!r} <= X".format(other), lambda x: other <= x
)
XObject.__rpow__ = lambda self, other: self.bind(
    lambda: "{0!r} ** X".format(other), lambda x: other ** x
)

X = XObject()


class Matcher(object):
    def __init__(self, pattern=None):
        self.pattern = pattern

    def __call__(self, pattern):
        return Matcher(pattern)

    def __rshift__(self, action):
        return Matchline(self.pattern, action)


class Matchline(object):
    def __init__(self, pattern, action):
        self.pattern = pattern
        self.action = action

    def __repr__(self):
        return "{!r} => {!r}".format(self.pattern, self.action)


m = Matcher()


class CaseError(Exception):
    pass


class caseof(object):
    def __init__(self, value, cases=None, *, default=NoDefault, strict=True):
        self.value = value
        self.cases = cases or []
        self.default = default
        self.strict = strict

    def __or__(self, other):
        if not isinstance(other, Matchline):
            raise CaseError("{!r} is not Matchline".format(other))
        return caseof(
            self.value, self.cases + [other], default=self.default, strict=self.strict
        )

    def __invert__(self):
        args = []
        for case in self.cases:
            pattern, action = case.pattern, case.action
            if isinstance(action, XObject):
                action = action._func or (lambda x: x)
            args += [pattern, action]

        return match(self.value, *args, self.default, self.strict)
