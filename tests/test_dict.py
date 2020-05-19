from xpattern import X
from xpattern import _
from xpattern import caseof
from xpattern import m


# fmt: off
def test_match_dict():
    pet = {"type": "dog", "details": {"age": 3}}

    assert ~(caseof(pet) | m({"details": {"age": _}}) >> (lambda age: age)) == 3
    assert ~(caseof(pet) | m({_: {"age": _}}) >> (lambda a, b: (a, b))) == ("details", 3)


def test_wild_dicts():
    data = [
        {"type": "dog", "dog-name": "fuffy", "info": {"age": 2}},
        {"type": "pet", "dog-name": "puffy", "info": {"age": 1}},
        {"type": "cat", "cat-name": "buffy", "cat-info": {"age": 3}},
    ]

    ages = [
        ~(caseof(row) | m({_: {"age": int}}) >> (lambda field, age: age))
        for row in data
    ]
    average_age = sum(ages) / len(ages)
    assert average_age == (2 + 1 + 3) / 3

    names = [
        ~(caseof(row) | m({"type": _, _: str}) >> (lambda type, name_field, name: name))
        for row in data
    ]
    assert names == ["fuffy", "puffy", "buffy"]


def test_with_xobject_action():
    pet = {"type": "dog", "details": {"age": 3}}

    assert ~(caseof(pet) | m({"details": {"age": _}}) >> X) == 3
    assert ~(caseof(pet) | m({_: {"age": _}}) >> X[0].upper()) == "DETAILS"
