# Xpattern: Pattern Matching with XObject.

![GitHub](https://img.shields.io/github/license/zen-xu/xpattern)
![Tests](https://github.com/zen-xu/xpattern/workflows/Tests/badge.svg?branch=master)
[![PyPI version](https://badge.fury.io/py/xpattern.svg)](https://badge.fury.io/py/xpattern)

> `xpattern` is inspired by [hask](https://github.com/billpmurphy/hask), [pipetools](https://github.com/0101/pipetools),
[pampy](https://github.com/santinic/pampy/), and with `xpattern` your code will be more readable and graceful!


## Let's play now
> Each pattern matchline evaluated in the order they appear.

```python
from xpattern import caseof
from xpattern import m


~(caseof(v)
    | m(pattern_1) >> action_1
    | m(pattern_2) >> action_2
)
```

`caseof` is lazy, so you need to add `~` operator to run it!

### Write a Fibonacci

> The operator `_` means "match everything"

```python
from xpattern import _
from xpattern import caseof
from xpattern import m


def fibonacci(n):
    return ~(caseof(n)
        | m(1) >> 1
        | m(2) >> 1
        | m(_) >> (lambda x: fibonacci(x - 1) + fibonacci(x - 2))
    )
```

### Write a Lisp calculator
```python
from functools import reduce

from xpattern import _
from xpattern import REST
from xpattern import caseof
from xpattern import m


def lisp(exp):
    return ~(caseof(exp)
        | m(int)            >> (lambda x: x)
        | m(callable)       >> (lambda x: x)
        | m(callable, REST) >> (lambda f, rest: f(*map(lisp, rest)))
        | m(tuple)          >> (lambda t: list(map(lisp, t)))
    )

plus = lambda a, b: a + b
minus = lambda a, b: a - b
lisp((plus, 1, 2))                  # => 3
lisp((plus, 1 (minus, 4, 2)))       # => 3
lisp((reduce, plus, (range, 10)))   # => 45
```

### You can match so many things!
```python
~(caseof(x)
    | m(3)         >> "this matches the number 3"
    | m(int)       >> "matches any integer"
    | m(str, int)  >> (lambda a, b: "a tuple (a, b) you can use in a function")
    | m(1, 2, _)   >> "any list of 3 elements that begins with [1, 2]"
    | m({"x", _})  >> "any dict with a key 'x' and any value associated"
    | m(_)         >> "anything else"
)
```

### Match [HEAD, TAIL]

```python
from xpattern import _
from xpattern import HEAD
from xpattern import TAIL
from xpattern import caseof
from xpattern import m


x = [1, 2, 3]

~(caseof(x)
    | m(1, TAIL) >> (lambda t: t)             # => [2, 3]
)

~(caseof(x)
    | m(HEAD, TAIL) >> (lambda h, t: (h, t))  # => [1, [2, 3]]
)
```

### More pattern cases

> Your can visit repo [pampy](https://github.com/santinic/pampy/) get more pattern cases, `xpattern` is *Syntactic Sugar* of `pampy`


### Why name `Xpattern`, what's `X` mean?

> `X` means `XObject` !!!
>
> `XObject` is a *Syntactic Sugar* of `lambda` function

```python
from xpattern import X
from xpattern import caseof
from xpattern import m


~(caseof(1)
    | m(1) >> X + 1       # => 2
)

~(caseof("apple")
    | m(str) >> X.upper()  # => "APPLE"
)

~(caseof([1, 2, 3])
    | m(1, 2, 3) >> X[2]   # => 3
)

~(caseof([1, 2, 3])
    | m(1, 2, 3) >> X + [4, 5, 6]   # => [1, 2, 3, 4, 5, 6]
)

~(caseof(9)
    | m(int) >> X + X ** (X << 2) % 2 / 3 - X  # => 0.333333333
)

~(caseof(1)
    | m(int) >> X._in_([1, 2, 3])   # => True
)

~(caseof(lambda x, y: x + y)
    | m(callable) >> X(1, 2)   # => 3
)
```

| Operation             | Syntax                                     |
| --------------------- | ------------------------------------------ |
| Addition              | `X + 1`                                    |
| Call                  | `X(a, b, c)`                               |
| Concatenation         | `X + [1, 2, 3]`                            |
| Containment Test      | `X._in_( [1, 2, 3] )`                    |
| Contains              | `X._contains_(1)`                          |
| Division              | `X / 2` or `X // 2`                        |
| Bitwise And           | `X & 2`                                    |
| Bitwise Exclusive Or  | `X ^ 2`                                    |
| Bitwise Inversion     | `~X`                                       |
| Bitwise Or            | `X \| 2`                                    |
| Exponentiation        | `X ** 2`                                   |
| Identity              | `X._is_(2)`                                |
| Indexing              | `X[k]`                                     |
| Left Shift            | `X << 2`                                   |
| Modulo                | `X % 2`                                    |
| Multiplication        | `X * 2`                                    |
| Matrix Multiplication | `X @ matrix`                               |
| Negation (Arithmetic) | `-X`                                       |
| Negation (Logical)    | `X._not()`                                 |
| Positive              | `+X`                                       |
| Right Shift           | `X >> 2`                                   |
| Subtraction           | `X - 2`                                    |
| Ordering              | `X < 2` or `X <= 2` or `X > 2` or `X >= 2` |
| Equality              | `X == 2`                                   |
| Difference            | `X != 2`                                   |
