from collections.abc import Iterable

from pampy import MatchError
from pampy import _
from pampy.helpers import BoxedArgs
from pampy.pampy import NoDefault
from pampy.pampy import match_value
from pampy.pampy import run as pampy_run

from ._xobject import Pipe
from ._xobject import XObject
from ._xobject import pipe


class Matcher(object):
    def __init__(self, pattern=None):
        self.pattern = pattern

    def __call__(self, pattern, *external_patterns):
        if external_patterns:
            pattern = [pattern] + list(external_patterns)

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


def run(action, var):
    if isinstance(action, Pipe):
        if isinstance(var, BoxedArgs):
            var = var.get()
        if isinstance(var, Iterable) and len(var) == 1:
            var = var[0]
        return action(var)
    return pampy_run(action, var)


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
        patterns = []
        for case in self.cases:
            pattern, action = case.pattern, case.action
            patterns.append(pattern)

            if isinstance(action, XObject):
                action = pipe | action or (lambda x: x)

            matched_as_value, args = match_value(pattern, self.value)
            if matched_as_value:
                lambda_args = args if len(args) > 0 else BoxedArgs(self.value)
                return run(action, lambda_args)

        if self.default is NoDefault and self.strict is False:
            default = False
        else:
            default = self.default

        if default is NoDefault:
            if _ not in patterns:
                raise MatchError(
                    "'_' not provided. This case is not handled:\n%s" % str(self.value)
                )
        else:
            return default
