from typing import Set, List, Iterator, Dict
from unittest import mock

import pytest

from bootstrap import Stream, identity, Optional


# pylint: disable=too-many-lines
def test_constructor_raise_type_error():
    with pytest.raises(TypeError):
        Stream()  # pylint: disable=abstract-class-instantiated


def test_of_iterable():
    actual = Stream.of('abc')

    assert list(actual) == ['a', 'b', 'c']


def test_of_list():
    actual = Stream.of([1, 2, 3])

    assert list(actual) == [1, 2, 3]


def test_of_varargs():
    actual = Stream.of(1, 2, 3)

    assert list(actual) == [1, 2, 3]


def test_of_no_args():
    actual = Stream.of()

    assert not list(actual)


def test_empty():
    actual = Stream.empty()

    assert not list(actual)


def test_generate_lazy():
    mock_supplier = mock.Mock()
    mock_supplier.side_effect = [1, 2, 3, 4, 5]

    actual = Stream.generate(mock_supplier)

    assert len(mock_supplier.mock_calls) == 0  # lazy
    assert list(actual.limit(3)) == [1, 2, 3]
    assert len(mock_supplier.mock_calls) == 3


def test_rangen():
    actual = Stream.range(3)

    assert list(actual) == [0, 1, 2]


def test_range_between():
    actual = Stream.range(3, 6)

    assert list(actual) == [3, 4, 5]


def test_range_step():
    actual = Stream.range(0, 6, 2)

    assert list(actual) == [0, 2, 4]


def test_filter():
    stream = Stream.range(10)

    actual = stream.filter(lambda x: x % 2 == 0)

    assert list(actual) == [0, 2, 4, 6, 8]


def test_filter_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)
    mock_predicate = mock.Mock()
    mock_predicate.side_effect = [True, False, True]

    actual = stream.filter(mock_predicate)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_predicate.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_map():
    stream = Stream.of('abc')

    actual = stream.map(str.upper)

    assert list(actual) == ['A', 'B', 'C']


def test_map_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_mapper = mock.Mock()
    mock_mapper.side_effect = ['A', 'B', 'C']
    stream = Stream.of(mock_iterable)

    actual = stream.map(mock_mapper)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == ['A', 'B', 'C']
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_mapper.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_flat_map():
    stream = Stream.of('abc')

    actual = stream.flat_map(lambda x: (x, x.upper()))

    assert list(actual) == ['a', 'A', 'b', 'B', 'c', 'C']


def test_flat_map_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_mapper = mock.Mock()
    mock_mapper.side_effect = [(1, 'A'), (2, 'B'), (3, 'C')]
    stream = Stream.of(mock_iterable)

    actual = stream.flat_map(mock_mapper)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 'A', 2, 'B', 3, 'C']
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_mapper.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_distinct():
    stream = Stream.of('abAbCc')

    actual = stream.distinct()

    assert list(actual) == ['a', 'b', 'A', 'C', 'c']


def test_distinct_comparator():
    stream = Stream.of('abAbCc')

    actual = stream.distinct(str.upper)

    assert list(actual) == ['a', 'b', 'C']


def test_distinct_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_comparator = mock.Mock()
    mock_comparator.side_effect = [1, 0, 1]
    stream = Stream.of(mock_iterable)

    actual = stream.distinct(mock_comparator)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 2]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_comparator.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_sorted():
    stream = Stream.of('bca')

    actual = stream.sorted()

    assert list(actual) == ['a', 'b', 'c']


def test_sorted_desc():
    stream = Stream.of('bca')

    actual = stream.sorted(reverse=True)

    assert list(actual) == ['c', 'b', 'a']


def test_sorted_comparator():
    stream = Stream.of('aaa', 'b', 'cc')

    actual = stream.sorted(len)

    assert list(actual) == ['b', 'cc', 'aaa']


def test_sorted_comparator_desc():
    stream = Stream.of('aaa', 'b', 'cc')

    actual = stream.sorted(len, reverse=True)

    assert list(actual) == ['aaa', 'cc', 'b']


def test_sorted_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_comparator = mock.Mock()
    mock_comparator.side_effect = [2, 3, 1]
    stream = Stream.of(mock_iterable)

    actual = stream.sorted(mock_comparator, reverse=True)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [2, 1, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_comparator.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_reversed():
    stream = Stream.of(1, 3, 2)

    actual = stream.reversed()

    assert list(actual) == [2, 3, 1]


def test_reversed_generator():  # generator is not reversible
    stream = Stream.of((x for x in (1, 3, 2)))

    actual = stream.reversed()

    assert list(actual) == [2, 3, 1]


def test_reversed_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    actual = stream.reversed()

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [3, 2, 1]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_peek():
    mock_consumer = mock.Mock()
    stream = Stream.of(1, 2, 3)

    actual = stream.peek(mock_consumer)

    assert list(actual) == [1, 2, 3]
    assert mock_consumer.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_peek_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_consumer = mock.Mock()
    stream = Stream.of(mock_iterable)

    actual = stream.peek(mock_consumer)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_consumer.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_enumerate():
    stream = Stream.of('abc')

    actual = stream.enumerate()

    assert list(actual) == [(0, 'a'), (1, 'b'), (2, 'c')]


def test_enumerate_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    actual = stream.enumerate()

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [(0, 1), (1, 2), (2, 3)]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_limit():
    stream = Stream.of(1, 2, 3, 4, 5)

    actual = stream.limit(3)

    assert list(actual) == [1, 2, 3]


def test_limit_generator():
    stream = Stream.of((x for x in (1, 2, 3, 4, 5)))

    actual = stream.limit(3)

    assert list(actual) == [1, 2, 3]


def test_limit_more():
    stream = Stream.of(1, 2, 3)

    actual = stream.limit(5)

    assert list(actual) == [1, 2, 3]


def test_limit_zero():
    stream = Stream.of(1, 2, 3)

    actual = stream.limit(0)

    assert not list(actual)


def test_limit_less():
    stream = Stream.of(1, 2, 3)

    actual = stream.limit(-1)

    assert not list(actual)


def test_limit_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3, 4, 5]
    stream = Stream.of(mock_iterable)

    actual = stream.limit(3)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 3
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 3
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 3


def test_limit_more_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    actual = stream.limit(5)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_skip():
    stream = Stream.of(1, 2, 3, 4, 5)

    actual = stream.skip(3)

    assert list(actual) == [4, 5]


def test_skip_generator():
    stream = Stream.of((x for x in (1, 2, 3, 4, 5)))

    actual = stream.skip(3)

    assert list(actual) == [4, 5]


def test_skip_more():
    stream = Stream.of(1, 2, 3)

    actual = stream.skip(5)

    assert not list(actual)


def test_skip_more_generator():
    stream = Stream.of((x for x in (1, 2, 3,)))

    actual = stream.skip(5)

    assert not list(actual)


def test_skip_less():
    stream = Stream.of(1, 2, 3)

    actual = stream.skip(-1)

    assert list(actual) == [1, 2, 3]


def test_skip_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3, 4, 5]
    stream = Stream.of(mock_iterable)

    actual = stream.skip(3)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [4, 5]
    assert len(mock_iterable.mock_calls) == 6  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 6
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 6


def test_skip_more_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2]
    stream = Stream.of(mock_iterable)

    actual = stream.skip(3)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert not list(actual)
    assert len(mock_iterable.mock_calls) == 3  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 3
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 3


def test_take_while():
    stream = Stream.of(1, 2, 3, 2, 1)

    actual = stream.take_while(lambda x: x < 3)

    assert list(actual) == [1, 2]


def test_take_while_nothing():
    stream = Stream.of(1, 2, 3)

    actual = stream.take_while(lambda x: x < 0)

    assert not list(actual)


def test_take_while_all():
    stream = Stream.of(1, 2, 3)

    actual = stream.take_while(lambda x: x < 5)

    assert list(actual) == [1, 2, 3]


def test_take_while_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3, 4]
    mock_predicate = mock.Mock()
    mock_predicate.side_effect = [True, True, False, True]
    stream = Stream.of(mock_iterable)

    actual = stream.take_while(mock_predicate)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 2]
    assert len(mock_iterable.mock_calls) == 3
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 3
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 3
    assert mock_predicate.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_drop_while():
    stream = Stream.of(1, 2, 3, 2, 1)

    actual = stream.drop_while(lambda x: x < 3)

    assert list(actual) == [3, 2, 1]


def test_drop_while_all():
    stream = Stream.of(1, 2, 3)

    actual = stream.drop_while(lambda x: x < 0)

    assert list(actual) == [1, 2, 3]


def test_drop_while_nothing():
    stream = Stream.of(1, 2, 3)

    actual = stream.drop_while(lambda x: x < 5)

    assert not list(actual)


def test_drop_while_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3, 4]
    mock_predicate = mock.Mock()
    mock_predicate.side_effect = [True, True, False, True]
    stream = Stream.of(mock_iterable)

    actual = stream.drop_while(mock_predicate)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [3, 4]
    assert len(mock_iterable.mock_calls) == 5  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 5
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 5
    assert mock_predicate.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_union():
    stream1 = Stream.of(1, 2, 3)
    stream2 = Stream.of('abc')

    actual = stream1.union(stream2)

    assert list(actual) == [1, 2, 3, 'a', 'b', 'c']


def test_union_lazy():
    mock_iterable1 = IterableMock()
    mock_iterable1.side_effect = [1, 2, 3]
    stream1 = Stream.of(mock_iterable1)
    mock_iterable2 = IterableMock()
    mock_iterable2.side_effect = [10, 20, 30]
    stream2 = Stream.of(mock_iterable2)

    actual = stream1.union(stream2)

    assert len(mock_iterable1.mock_calls) == 0  # lazy
    assert len(mock_iterable2.mock_calls) == 0  # lazy
    assert list(actual) == [1, 2, 3, 10, 20, 30]
    assert is_consumed(actual)
    assert len(mock_iterable1.mock_calls) == 4  # +1 raise StopIteration
    assert len(mock_iterable2.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(stream1)
    assert is_consumed(stream2)
    assert len(mock_iterable1.mock_calls) == 4
    assert len(mock_iterable2.mock_calls) == 4


def test_transform():
    stream = Stream.of('abc')

    actual = stream.transform(lambda x: x.map(str.upper))

    assert list(actual) == ['A', 'B', 'C']


def test_transform_lazy():
    def stub(input_stream):
        assert input_stream == stream
        return input_stream.map(str.upper)

    mock_iterable = IterableMock()
    mock_iterable.side_effect = ['a', 'b', 'c']
    stream = Stream.of(mock_iterable)

    actual = stream.transform(stub)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == ['A', 'B', 'C']
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_materialize():
    stream = Stream.of('abc')

    actual = stream.materialize()

    assert list(actual) == ['a', 'b', 'c']
    assert list(actual) == ['a', 'b', 'c']
    child1 = actual.map(lambda x: (x, x.upper()))
    assert list(child1) == [('a', 'A'), ('b', 'B'), ('c', 'C')]
    assert is_consumed(child1)
    child2 = actual.map(lambda x: (x, ord(x)))
    assert list(child2) == [('a', 97), ('b', 98), ('c', 99)]
    assert is_consumed(child2)


def test_materialize_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = ['a', 'b', 'c']
    stream = Stream.of(mock_iterable)

    actual = stream.materialize()

    assert len(mock_iterable.mock_calls) == 4  # lazy / +1 raise StopIteration
    assert list(actual) == ['a', 'b', 'c']
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert list(actual) == ['a', 'b', 'c']
    assert len(mock_iterable.mock_calls) == 4
    assert list(actual.map(str.upper)) == ['A', 'B', 'C']
    assert len(mock_iterable.mock_calls) == 4
    assert list(actual.map(str.lower)) == ['a', 'b', 'c']
    assert len(mock_iterable.mock_calls) == 4


def test_for_each():
    stream = Stream.of('abc')
    mock_consumer = mock.Mock()

    stream.for_each(mock_consumer)

    assert mock_consumer.call_args_list == [mock.call('a'), mock.call('b'), mock.call('c')]


def test_for_each_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_consumer = mock.Mock()
    stream = Stream.of(mock_iterable)

    stream.for_each(mock_consumer)

    assert len(mock_iterable.mock_calls) == 4  # terminal operation / +1 raise StopIteration
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_consumer.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_collect():
    stream = Stream.of('abca')

    actual = stream.collect(set)

    assert isinstance(actual, Set)
    assert actual == {'a', 'b', 'c'}


def test_collector_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    actual = stream.collect(list)

    assert isinstance(actual, List)
    assert actual == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 4  # terminal operation / +1 raise StopIteration
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_iterator():
    stream = Stream.of('abc')

    actual = stream.iterator()

    assert isinstance(actual, Iterator)
    assert next(actual) == 'a'
    assert next(actual) == 'b'
    assert next(actual) == 'c'
    with pytest.raises(StopIteration):
        next(actual)


def test_iterator_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    actual = stream.iterator()

    assert isinstance(actual, Iterator)
    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert is_consumed(stream)  # terminal operation
    assert next(actual) == 1
    assert len(mock_iterable.mock_calls) == 1
    assert is_consumed(stream)
    assert next(actual) == 2
    assert len(mock_iterable.mock_calls) == 2
    assert is_consumed(stream)
    assert next(actual) == 3
    assert len(mock_iterable.mock_calls) == 3
    assert is_consumed(stream)
    with pytest.raises(StopIteration):
        next(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)


def test_to_list():
    stream = Stream.of('abc')

    actual = stream.to_list()

    assert isinstance(actual, List)
    assert actual == ['a', 'b', 'c']


def test_to_set():
    stream = Stream.of('abcabc')

    actual = stream.to_set()

    assert isinstance(actual, Set)
    assert actual == {'a', 'b', 'c'}


def test_to_dict():
    stream = Stream.of(('a', 1), ('b', 2), ('c', 3))

    actual = stream.to_dict()

    assert isinstance(actual, Dict)
    assert actual == {'a': 1, 'b': 2, 'c': 3}


def test_reduce():
    stream = Stream.of(1, 2, 3)

    actual = stream.reduce(lambda a, x: a + x)

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 6


def test_reduce_empty():
    stream = Stream.of()

    actual = stream.reduce(lambda a, x: a + x)

    assert isinstance(actual, Optional)
    assert actual.is_empty()


def test_reduce_initial():
    stream = Stream.of(1, 2, 3)

    actual = stream.reduce(lambda a, x: a + x, 10)

    assert not isinstance(actual, Optional)
    assert actual == 16


def test_reduce_initial_empty():
    stream = Stream.of()

    actual = stream.reduce(lambda a, x: a + x, 10)

    assert not isinstance(actual, Optional)
    assert actual == 10


def test_reduce_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_accumulator = mock.Mock()
    mock_accumulator.side_effect = [10, 20]
    stream = Stream.of(mock_iterable)

    actual = stream.reduce(mock_accumulator)

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 20
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(stream)
    assert mock_accumulator.call_args_list == [mock.call(1, 2), mock.call(10, 3)]


def test_min():
    stream = Stream.of(3, 1, 2) \
        .map(identity)

    actual = stream.min()

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 1


def test_min_empty():
    stream = Stream.of()

    actual = stream.min()

    assert isinstance(actual, Optional)
    assert actual.is_empty()


def test_min_comparator():
    stream = Stream.of('aaa', 'c', 'bb')

    actual = stream.min(len)

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 'c'


def test_min_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_comparator = mock.Mock()
    mock_comparator.side_effect = [3, -1, 0]
    stream = Stream.of(mock_iterable)

    actual = stream.min(mock_comparator)

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 2
    assert len(mock_iterable.mock_calls) == 4  # terminal operation / +1 raise StopIteration
    assert is_consumed(stream)
    assert mock_comparator.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_max():
    stream = Stream.of(2, 1, 3)

    actual = stream.max()

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 3


def test_max_empty():
    stream = Stream.of()

    actual = stream.max()

    assert isinstance(actual, Optional)
    assert actual.is_empty()


def test_max_comparator():
    stream = Stream.of('aaa', 'c', 'bb') \
        .map(identity)

    actual = stream.max(len)

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 'aaa'


def test_max_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_comparator = mock.Mock()
    mock_comparator.side_effect = [3, -1, 0]
    stream = Stream.of(mock_iterable)

    actual = stream.max(mock_comparator)

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 1
    assert len(mock_iterable.mock_calls) == 4  # terminal operation / +1 raise StopIteration
    assert is_consumed(stream)
    assert mock_comparator.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_count():
    stream = Stream.of(1, 3, 5)

    actual = stream.count()

    assert actual == 3


def test_count_empty():
    stream = Stream.empty()

    actual = stream.count()

    assert actual == 0


def test_count_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    actual = stream.count()

    assert actual == 3
    assert len(mock_iterable.mock_calls) == 4  # terminal operation / +1 raise StopIteration
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_any_match_true():
    stream = Stream.of(True, True, True)

    actual = stream.any_match()

    assert actual


def test_any_match_partial():
    stream = Stream.of(False, True, False)

    actual = stream.any_match()

    assert actual


def test_any_match_false():
    stream = Stream.of(False, False, False)

    actual = stream.any_match()

    assert not actual


def test_any_match_predicate():
    stream = Stream.of('a', '1', 'b')

    actual = stream.any_match(str.isnumeric)

    assert actual


def test_any_match_predicate_nothing():
    stream = Stream.of('a', '1', 'b')

    actual = stream.any_match(str.isupper)

    assert not actual


def test_any_match_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_predicate = mock.Mock()
    mock_predicate.side_effect = [False, True, True]
    stream = Stream.of(mock_iterable)

    actual = stream.any_match(mock_predicate)

    assert actual
    assert len(mock_iterable.mock_calls) == 2  # lazy
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 2
    assert mock_predicate.call_args_list == [mock.call(1), mock.call(2)]


def test_all_match_true():
    stream = Stream.of(True, True, True)

    actual = stream.all_match()

    assert actual


def test_all_match_partial():
    stream = Stream.of(False, False, True)

    actual = stream.all_match()

    assert not actual


def test_all_match_false():
    stream = Stream.of(False, False, False)

    actual = stream.all_match()

    assert not actual


def test_all_match_predicate():
    stream = Stream.of('1', '2', '3')

    actual = stream.all_match(str.isnumeric)

    assert actual


def test_all_match_predicate_nothing():
    stream = Stream.of('a', '1', '2')

    actual = stream.all_match(str.isnumeric)

    assert not actual


def test_all_match_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_predicate = mock.Mock()
    mock_predicate.side_effect = [True, True, False]
    stream = Stream.of(mock_iterable)

    actual = stream.all_match(mock_predicate)

    assert not actual
    assert len(mock_iterable.mock_calls) == 3  # lazy
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 3
    assert mock_predicate.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_none_match_true():
    stream = Stream.of(True, True, True)

    actual = stream.none_match()

    assert not actual


def test_none_match_partial():
    stream = Stream.of(False, False, True)

    actual = stream.none_match()

    assert not actual


def test_none_match_false():
    stream = Stream.of(False, False, False)

    actual = stream.none_match()

    assert actual


def test_none_match_predicate():
    stream = Stream.of('1', '2', '3')

    actual = stream.none_match(str.isalpha)

    assert actual


def test_none_match_predicate_nothing():
    stream = Stream.of('a', '1', '2')

    actual = stream.none_match(str.isalpha)

    assert not actual


def test_none_match_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_predicate = mock.Mock()
    mock_predicate.side_effect = [False, False, False]
    stream = Stream.of(mock_iterable)

    actual = stream.none_match(mock_predicate)

    assert actual
    assert len(mock_iterable.mock_calls) == 4  # lazy
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_predicate.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_find_first():
    stream = Stream.of(2, 3, 4)

    actual = stream.find_first()

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 2


def test_find_first_empty():
    stream = Stream.empty()

    actual = stream.find_first()

    assert isinstance(actual, Optional)
    assert actual.is_empty()


def test_find_first_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    actual = stream.find_first()

    assert isinstance(actual, Optional)
    assert actual.is_present()
    assert actual.get() == 1
    assert len(mock_iterable.mock_calls) == 1  # terminal operation
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 1


def test_key_by():
    stream = Stream.of('abc')

    actual = stream.key_by(ord)

    assert list(actual) == [(97, 'a'), (98, 'b'), (99, 'c')]


def test_key_by_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    mock_mapper = mock.Mock()
    mock_mapper.side_effect = ['a', 'b', 'c']
    stream = Stream.of(mock_iterable)

    actual = stream.key_by(mock_mapper)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [('a', 1), ('b', 2), ('c', 3)]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_mapper.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_keys():
    stream = Stream.of(('a', 1), ('b', 2), ('c', 3))

    actual = stream.keys()

    assert list(actual) == ['a', 'b', 'c']


def test_keys_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [('a', 1), ('b', 2), ('c', 3)]
    stream = Stream.of(mock_iterable)

    actual = stream.keys()

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == ['a', 'b', 'c']
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_values():
    stream = Stream.of([('a', 1), ('b', 2), ('c', 3)])

    actual = stream.values()

    assert list(actual) == [1, 2, 3]


def test_values_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [('a', 1), ('b', 2), ('c', 3)]
    stream = Stream.of(mock_iterable)

    actual = stream.values()

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_map_values():
    stream = Stream.of((1, 'a'), (2, 'b'), (3, 'c'))

    actual = stream.map_values(str.upper)

    assert list(actual) == [(1, 'A'), (2, 'B'), (3, 'C')]


def test_map_values_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [('a', 1), ('b', 2), ('c', 3)]
    mock_mapper = mock.Mock()
    mock_mapper.side_effect = [10, 20, 30]
    stream = Stream.of(mock_iterable)

    actual = stream.map_values(mock_mapper)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [('a', 10), ('b', 20), ('c', 30)]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_mapper.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_flat_map_values():
    stream = Stream.of((1, 'a'), (2, 'bc'))

    actual = stream.flat_map_values(identity)

    assert list(actual) == [(1, 'a'), (2, 'b'), (2, 'c')]


def test_flat_map_values_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [('a', 1), ('b', 2), ('c', 3)]
    mock_mapper = mock.Mock()
    mock_mapper.side_effect = [[10, 20], [30], []]
    stream = Stream.of(mock_iterable)

    actual = stream.flat_map_values(mock_mapper)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [('a', 10), ('a', 20), ('b', 30)]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_mapper.call_args_list == [mock.call(1), mock.call(2), mock.call(3)]


def test_group_by():
    stream = Stream.of('aa', 'ccc', 'bb')

    actual = stream.group_by(len)

    assert list(actual) == [(2, ['aa', 'bb']), (3, ['ccc'])]


def test_group_by_empty():
    stream = Stream.of()

    actual = stream.group_by(len)

    assert not list(actual)


def test_group_by_downstream():
    stream = Stream.of('aa', 'ccc', 'bb')

    actual = stream.group_by(len, downstream=str.upper)

    assert list(actual) == [(2, ['AA', 'BB']), (3, ['CCC'])]


def test_group_by_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = ['a', 'b', 'c']
    mock_classifier = mock.Mock()
    mock_classifier.side_effect = [1, 2, 1]
    mock_downstream = mock.Mock()
    mock_downstream.side_effect = [10, 20, 30]
    stream = Stream.of(mock_iterable)

    actual = stream.group_by(mock_classifier, mock_downstream)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [(1, [10, 20]), (2, [30])]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_classifier.call_args_list == [mock.call('a'), mock.call('b'), mock.call('c')]
    assert mock_downstream.call_args_list == [mock.call('a'), mock.call('c'), mock.call('b')]


def test_group_by_key():
    stream = Stream.of((1, 'a'), (2, 'b'), (2, 'c'), (1, 'd'))

    actual = stream.group_by_key()

    assert list(actual) == [(1, ['a', 'd']), (2, ['b', 'c'])]


def test_group_by_key_downstream():
    stream = Stream.of((1, 'a'), (2, 'b'), (2, 'c'), (1, 'd'))

    actual = stream.group_by_key(str.upper)

    assert list(actual) == [(1, ['A', 'D']), (2, ['B', 'C'])]


def test_group_by_key_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [(1, 'a'), (2, 'b'), (2, 'c')]
    mock_downstream = mock.Mock()
    mock_downstream.side_effect = [10, 20, 30]
    stream = Stream.of(mock_iterable)

    actual = stream.group_by_key(mock_downstream)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [(1, [10]), (2, [20, 30])]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_downstream.call_args_list == [mock.call('a'), mock.call('b'), mock.call('c')]


def test_reduce_by_key():
    stream = Stream.of(('a', 1), ('b', 2), ('a', 3))

    actual = stream.reduce_by_key(lambda x, y: x + y)

    assert list(actual) == [('a', 4), ('b', 2)]


def test_reduce_by_key_initial():
    stream = Stream.of(('a', 1), ('b', 2), ('a', 3))

    actual = stream.reduce_by_key(lambda x, y: x + str(y), initial='0.')

    assert list(actual) == [('a', '0.13'), ('b', '0.2')]


def test_reduce_by_key_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [(1, 'a'), (2, 'b'), (2, 'c')]
    mock_accumulator = mock.Mock()
    mock_accumulator.side_effect = [10, 20, 30]
    stream = Stream.of(mock_iterable)

    actual = stream.reduce_by_key(mock_accumulator, 'd')

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(actual) == [(1, 10), (2, 30)]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(actual)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4
    assert mock_accumulator.call_args_list == [mock.call('d', 'a'), mock.call('d', 'b'), mock.call(20, 'c')]


def test_joining():
    stream = Stream.of('a', 'b', 'c')

    actual = stream.joining()

    assert isinstance(actual, str)
    assert actual == 'abc'


def test_joining_empty():
    stream = Stream.empty()

    actual = stream.joining()

    assert isinstance(actual, str)
    assert actual == ''


def test_joining_delimiter():
    stream = Stream.of(1, 2, 3)

    actual = stream.joining(', ', '[', ']')

    assert isinstance(actual, str)
    assert actual == '[1, 2, 3]'


def test_joining_delimiter_empty():
    stream = Stream.empty()

    actual = stream.joining(', ', '[', ']')

    assert isinstance(actual, str)
    assert actual == '[]'


def test_joining_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = ['a', 'b', 'c']
    stream = Stream.of(mock_iterable)

    actual = stream.joining()

    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert isinstance(actual, str)
    assert actual == 'abc'
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_pipeline_consumed():
    stream = Stream.of(1, 2, 3)

    assert list(stream) == [1, 2, 3]
    assert is_consumed(stream)


def test_pipeline_children_consumed():
    parent_stream = Stream.of(1, 2, 3)
    child_stream_a = parent_stream.map(lambda x: x + 1)
    child_stream_b = parent_stream.map(lambda x: x + 2)

    assert list(parent_stream) == [1, 2, 3]
    assert is_consumed(child_stream_a)
    assert is_consumed(child_stream_b)


def test_pipeline_parent_consumed():
    parent_stream = Stream.of(1, 2, 3)
    child_stream_a = parent_stream.map(lambda x: x + 1)
    child_stream_b = parent_stream.map(lambda x: x + 2)

    assert list(child_stream_a) == [2, 3, 4]
    assert is_consumed(parent_stream)
    assert is_consumed(child_stream_b)


def test_pipeline_consumed_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    stream = Stream.of(mock_iterable)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(stream) == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(stream)
    assert len(mock_iterable.mock_calls) == 4


def test_pipeline_children_consumed_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    parent_stream = Stream.of(mock_iterable)
    child_stream_a = parent_stream.map(lambda x: x + 1)
    child_stream_b = parent_stream.map(lambda x: x + 2)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(parent_stream) == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(child_stream_a)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(child_stream_b)
    assert len(mock_iterable.mock_calls) == 4


def test_pipeline_parent_consumed_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    parent_stream = Stream.of(mock_iterable)
    child_stream_a = parent_stream.map(lambda x: x + 1)
    child_stream_b = parent_stream.map(lambda x: x + 2)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(child_stream_a) == [2, 3, 4]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(parent_stream)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(child_stream_b)
    assert len(mock_iterable.mock_calls) == 4


def test_pipeline_children_deep_consumed_lazy():
    mock_iterable = IterableMock()
    mock_iterable.side_effect = [1, 2, 3]
    parent_stream = Stream.of(mock_iterable)
    child_stream_a = parent_stream.map(lambda x: x + 1)
    child_stream_b = child_stream_a.map(lambda x: x + 2)

    assert len(mock_iterable.mock_calls) == 0  # lazy
    assert list(parent_stream) == [1, 2, 3]
    assert len(mock_iterable.mock_calls) == 4  # +1 raise StopIteration
    assert is_consumed(child_stream_a)
    assert len(mock_iterable.mock_calls) == 4
    assert is_consumed(child_stream_b)
    assert len(mock_iterable.mock_calls) == 4


def is_consumed(stream: Stream) -> bool:
    with pytest.raises(ValueError) as e:
        # pylint: disable=singleton-comparison
        assert list(stream) == False  # show what return
    return str(e.value) == 'stream has already been operated upon or closed'


class IterableMock(mock.Mock):
    """ IterableMock is a subclass of Mock with iterable implementation """

    def __iter__(self):
        def func():
            try:
                while True:
                    yield self()
            except StopIteration:
                pass

        return iter(func())
