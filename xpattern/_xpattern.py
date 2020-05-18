from collections.abc import Iterable

from pampy import match
from pampy import match_value
from pampy.helpers import BoxedArgs
from pampy.pampy import NoDefault

from ._xobject import X
from ._xobject import XObject
from ._xobject import pipe


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
    def __init__(self, value, cases=None, default=NoDefault, strict=True):
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
                action = pipe | action or (lambda x: x)
            args += [pattern, action]

        return match(self.value, *args, default=self.default, strict=self.strict)
