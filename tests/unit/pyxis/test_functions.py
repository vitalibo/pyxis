import pytest

from pyxis import functions


# pylint: disable=missing-class-docstring
def test_require_not_none():
    obj = object()

    actual = functions.require_not_none(obj)

    assert hash(obj) == hash(actual)


def test_require_not_none_raise():
    with pytest.raises(ValueError) as e:
        functions.require_not_none(None)

    assert e.value.args == ()


def test_require_not_none_with_msg():
    obj = object()

    actual = functions.require_not_none(obj, 'foo')

    assert hash(obj) == hash(actual)


def test_require_not_none_raise_with_msg():
    with pytest.raises(ValueError) as e:
        functions.require_not_none(None, 'foo')

    assert e.value.args == ('foo',)


def test_is_none_false():
    actual = functions.is_none('foo')

    assert not actual


def test_is_none_true():
    actual = functions.is_none(None)

    assert actual


def test_not_none_false():
    actual = functions.not_none(None)

    assert not actual


def test_not_none_true():
    actual = functions.not_none('foo')

    assert actual


def test_identity():
    obj = object()

    actual = functions.identity(obj)

    assert hash(obj) == hash(actual)


def test_one_instance_only():
    class ClassA(metaclass=functions.SingletonMeta):
        pass

    obj1 = ClassA()
    obj2 = ClassA()

    assert obj1 is obj2


def test_multiple_classes():
    class ClassA(metaclass=functions.SingletonMeta):
        pass

    class ClassB(metaclass=functions.SingletonMeta):
        pass

    obj1 = ClassA()
    obj2 = ClassB()

    assert obj1 is not obj2


def test_unpack():
    unpacked = functions.unpack(lambda x, y: x + y)

    assert unpacked((1, 2)) == 3


def test_return_values_as_list():
    @functions.return_values_as(list)
    def func():
        yield from [1, 2, 3, 2, 1]

    actual = func()

    assert actual == [1, 2, 3, 2, 1]


def test_return_values_as_set():
    @functions.return_values_as(set)
    def func():
        yield from [1, 2, 3, 2, 1]

    actual = func()

    assert actual == {1, 2, 3}


def test_return_values_as_dict():
    @functions.return_values_as(dict)
    def func():
        yield from [('foo', 1), ('bar', 2), ('baz', 3)]

    actual = func()

    assert actual == {'foo': 1, 'bar': 2, 'baz': 3}


def test_function_apply():
    actual = functions.function(lambda x: x + 1)

    assert actual.apply(10) == 11


def test_function_compose():
    this = functions.function(lambda x: x + 1)
    other = functions.function(lambda x: x * 2)

    actual = this.compose(other)

    assert actual(10) == 21


def test_function_and_then():
    this = functions.function(lambda x: x + 1)
    other = functions.function(lambda x: x * 2)

    actual = this.and_then(other)

    assert actual(10) == 22


def test_function_call():
    actual = functions.function(lambda x: x + 1)

    assert actual(10) == 11


def test_function_rshift():
    this = functions.function(lambda x: x + 1)
    other = functions.function(lambda x: x * 2)

    actual = this << other

    assert actual(10) == 21


def test_function_lshift():
    this = functions.function(lambda x: x + 1)
    other = functions.function(lambda x: x * 2)

    actual = this >> other

    assert actual(10) == 22
