from collections.abc import Iterable

from pampy import MatchError
from pampy import _
from pampy.helpers import BoxedArgs
from pampy.helpers import UnderscoreType
from pampy.helpers import is_dataclass
from pampy.pampy import NoDefault
from pampy.pampy import match_value as pampy_match_value
from pampy.pampy import run as pampy_run

from ._xobject import Pipe
from ._xobject import XObject
from ._xobject import pipe


UnderscoreType.__rshift__ = lambda self, other: Matcher(self) >> other
UnderscoreType.__eq__ = lambda self, other: other.__class__ == self.__class__


class Matcher(object):
    def __init__(self, pattern=None):
        self.pattern = pattern

    def __call__(self, pattern, *external_patterns):
        if external_patterns:
            pattern = [pattern] + list(external_patterns)

        return Matcher(pattern)

    def __rshift__(self, action):
        return Matchline(self.pattern, action)

    def __getitem__(self, pattern):
        return Matcher(pattern)

    def __or__(self, other_matcher):
        def new_pattern(value):
            return (
                match_value(self.pattern, value)[0]
                or match_value(other_matcher.pattern, value)[0]
            )

        return Matcher(new_pattern)

    def __and__(self, other_matcher):
        def new_pattern(value):
            return (
                match_value(self.pattern, value)[0]
                and match_value(other_matcher.pattern, value)[0]
            )

        return Matcher(new_pattern)

    def __invert__(self):
        def new_pattern(value):
            return match_value(self.pattern, value)[0] ^ True

        return Matcher(new_pattern)


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


def match_value(pattern, value):
    if isinstance(pattern, XObject):
        return_value = pattern._x_func(value)
        if not isinstance(return_value, bool):
            raise MatchError(
                f"Warning! XObject matcher {pattern} is not returning a boolean"
                f", but instead {return_value}"
            )
        return return_value, []
    elif isinstance(pattern, dict):
        return match_dict(pattern, value)
    elif pattern == _:
        return True, [value]
    elif is_dataclass(pattern) and pattern.__class__ == value.__class__:
        return match_dict(pattern.__dict__, value.__dict__)

    return pampy_match_value(pattern, value)


def match_dict(pattern, value):
    if not isinstance(value, dict) or not isinstance(pattern, dict):
        return False, []

    total_extracted = []
    still_usable_value_keys = set(value.keys())
    still_usable_pattern_keys = set(pattern.keys())
    for pkey, pval in pattern.items():
        if pkey not in still_usable_pattern_keys:
            continue
        matched_left_and_right = False
        for vkey, vval in value.items():
            if vkey not in still_usable_value_keys:
                continue
            if pkey not in still_usable_pattern_keys:
                continue
            key_matched, key_extracted = match_value(pkey, vkey)
            if key_matched:
                value_matched, value_extracted = match_value(pval, vval)
                if value_matched:
                    total_extracted += key_extracted + value_extracted
                    matched_left_and_right = True
                    still_usable_pattern_keys.remove(pkey)
                    still_usable_value_keys.remove(vkey)
                    break
        if not matched_left_and_right:
            return False, []
    return True, total_extracted


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
        if isinstance(self.value, XObject):

            def wrapped(x, *args):
                if args:
                    x = [x] + list(args)
                return ~caseof(
                    x, cases=self.cases, default=self.default, strict=self.strict
                )

            return wrapped

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
