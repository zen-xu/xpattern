from itertools import chain


def set_name(name, f):
    try:
        f.__xobject_name__ = name
    except (AttributeError, UnicodeEncodeError):
        pass

    return f


def get_name(f):
    xobject_name = getattr(f, "__xobject_name__", None)

    if xobject_name:
        return xobject_name() if callable(xobject_name) else xobject_name

    return f.__name__ if hasattr(f, "__name__") else repr(f)


def repr_args(*args, **kwargs):
    return ", ".join(
        chain(map("{0!r}".format, args), map("{0[0]}={0[1]!r}".format, kwargs.items()))
    )


class Pipe(object):
    def __init__(self, func=None):
        self.func = func

    def __str__(self):
        return get_name(self.func)

    __repr__ = __str__

    @staticmethod
    def compose(first, second):
        name = lambda: "{0} |> {1}".format(get_name(first), get_name(second))

        def composite(*args, **kwargs):
            return second(first(*args, **kwargs))

        return set_name(name, composite)

    @classmethod
    def bind(cls, first, second):
        # fmt: off
        return cls(
            first if second is None else
            second if first is None else
            cls.compose(first, second)
        )
        # fmt: on

    def __or__(self, next_func):
        if isinstance(next_func, XObject):
            if next_func._x_func is None:
                next_func = lambda x: x
                set_name(lambda: "X", next_func)
            else:
                next_func = next_func._x_func

        return self.bind(self.func, next_func)

    def __call__(self, *args, **kwargs):
        result = self.func(*args, **kwargs)
        if isinstance(result, XObject):
            return (pipe | result)(*args, **kwargs)
        return result


pipe = Pipe()


class XObject(object):
    def __init__(self, func=None):
        self._x_func = func
        set_name(lambda: get_name(func) if func else "X", self)

    def _x_bind(self, name, func):
        set_name(name, func)
        return XObject((self._x_func | func) if self._x_func else (pipe | func))

    def __repr__(self):
        return get_name(self)

    def __pos__(self):
        return self._x_bind(lambda: "+X", lambda x: +x)

    def __neg__(self):
        return self._x_bind(lambda: "-X", lambda x: -x)

    def __invert__(self):
        return self._x_bind(lambda: "~X", lambda x: ~x)

    def __add__(self, other):
        return self._x_bind(lambda: "X + {0!r}".format(other), lambda x: x + other)

    def __sub__(self, other):
        return self._x_bind(lambda: "X - {0!r}".format(other), lambda x: x - other)

    def __mul__(self, other):
        return self._x_bind(lambda: "X * {0!r}".format(other), lambda x: x * other)

    def __floordiv__(self, other):
        return self._x_bind(lambda: "X // {0!r}".format(other), lambda x: x // other)

    def __truediv__(self, other):
        return self._x_bind(lambda: "X / {0!r}".format(other), lambda x: x / other)

    def __mod__(self, other):
        return self._x_bind(lambda: "X % {0!r}".format(other), lambda x: x % other)

    def __pow__(self, other):
        return self._x_bind(lambda: "X ** {0!r}".format(other), lambda x: x ** other)

    def __lshift__(self, other):
        return self._x_bind(lambda: "X << {0!r}".format(other), lambda x: x << other)

    def __rshift__(self, other):
        return self._x_bind(lambda: "X >> {0!r}".format(other), lambda x: x >> other)

    def __and__(self, other):
        return self._x_bind(lambda: "X & {0!r}".format(other), lambda x: x & other)

    def __xor__(self, other):
        return self._x_bind(lambda: "X ^ {0!r}".format(other), lambda x: x ^ other)

    def __or__(self, other):
        return self._x_bind(lambda: "X | {0!r}".format(other), lambda x: x | other)

    def __matmul__(self, other):
        return self._x_bind(lambda: "X @ {0!r}".format(other), lambda x: x @ other)

    def __lt__(self, other):
        return self._x_bind(lambda: "X < {0!r}".format(other), lambda x: x < other)

    def __le__(self, other):
        return self._x_bind(lambda: "X <= {0!r}".format(other), lambda x: x <= other)

    def __gt__(self, other):
        return self._x_bind(lambda: "X > {0!r}".format(other), lambda x: x > other)

    def __ge__(self, other):
        return self._x_bind(lambda: "X >= {0!r}".format(other), lambda x: x >= other)

    def __eq__(self, other):
        return self._x_bind(lambda: "X == {0!r}".format(other), lambda x: x == other)

    def __ne__(self, other):
        return self._x_bind(lambda: "X != {0!r}".format(other), lambda x: x != other)

    def __radd__(self, other):
        return self._x_bind(lambda: "{0!r} + X".format(other), lambda x: other + x)

    def __rsub__(self, other):
        return self._x_bind(lambda: "{0!r} - X".format(other), lambda x: other - x)

    def __rmul__(self, other):
        return self._x_bind(lambda: "{0!r} * X".format(other), lambda x: other * x)

    def __rfloordiv__(self, other):
        return self._x_bind(lambda: "{0!r} // X".format(other), lambda x: other // x)

    def __rtruediv__(self, other):
        return self._x_bind(lambda: "{0!r} / X".format(other), lambda x: other / x)

    def __rmod__(self, other):
        return self._x_bind(lambda: "{0!r} % X".format(other), lambda x: other % x)

    def __rpow__(self, other):
        return self._x_bind(lambda: "{0!r} ** X".format(other), lambda x: other ** x)

    def __rlshift__(self, other):
        return self._x_bind(lambda: "{0!r} << X".format(other), lambda x: other << x)

    def __rrshift__(self, other):
        return self._x_bind(lambda: "{0!r} >> X".format(other), lambda x: other >> x)

    def __rand__(self, other):
        return self._x_bind(lambda: "{0!r} & X".format(other), lambda x: other & x)

    def __rxor__(self, other):
        return self._x_bind(lambda: "{0!r} ^ X".format(other), lambda x: other ^ x)

    def __ror__(self, other):
        return self._x_bind(lambda: "{0!r} | X".format(other), lambda x: other | x)

    def __rmatmul__(self, other):
        return self._x_bind(lambda: "{0!r} @ X".format(other), lambda x: other @ x)

    def __rlt__(self, other):
        return self._x_bind(lambda: "{0!r} < X".format(other), lambda x: other < x)

    def __rle__(self, other):
        return self._x_bind(lambda: "{0!r} <= X".format(other), lambda x: other <= X)

    def __rgt__(self, other):
        return self._x_bind(lambda: "{0!r} > X".format(other), lambda x: other > x)

    def __rge__(self, other):
        return self._x_bind(lambda: "{0!r} >= X".format(other), lambda x: other >= X)

    def __req__(self, other):
        return self._x_bind(lambda: "{0!r} == X".format(other), lambda x: other == x)

    def __rne__(self, other):
        return self._x_bind(lambda: "{0!r} != X".format(other), lambda x: other != x)

    def __concat__(self, other):
        return self._x_bind(lambda: "X + {0!r}".format(other), lambda x: x + other)

    def __getattr__(self, name):
        return self._x_bind(lambda: "X.{0}".format(name), lambda x: getattr(x, name))

    def __getitem__(self, item):
        return self._x_bind(lambda: "X[{0!r}]".format(item), lambda x: x[item])

    def _in_(self, iterable):
        return self._x_bind(
            lambda: "X in {0!r}".format(iterable), lambda x: x in iterable
        )

    def _contains_(self, item):
        return self._x_bind(lambda: "{0!r} in X".format(item), lambda x: item in x)

    def _is_(self, item):
        return self._x_bind(lambda: "X is {0!r}".format(item), lambda x: x is item)

    def _not(self):
        return self._x_bind(lambda: "not X", lambda x: not x)

    def __call__(self, *args, **kwargs):
        name = lambda: "X(%s)" % repr_args(*args, **kwargs)
        return self._x_bind(name, lambda x: x(*args, **kwargs))

    def __hash__(self):
        return super(XObject, self).__hash__()


X = XObject()
