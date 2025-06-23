# -*- coding: utf-8 -*-

from itertools import islice

from .compact import T


T_ITEM = T.TypeVar("T_ITEM")


def batched(
    iterable: T.Iterable[T_ITEM],
    n: int,
    *,
    strict: bool = False,
) -> T.Iterator[list[T_ITEM]]:
    """
    Batch data into lists of length *n*. If the number of items in
    *iterable* is not divisible by *n*:

    - The last batch will be shorter if *strict* is ``False``.
    - :exc:`ValueError` will be raised if *strict* is ``True``.

    >>> list(batched('ABCDEFG', 3))
    [['A', 'B', 'C'], ['D', 'E', 'F'], ['G']]

    Args:
        iterable: An iterable of items of type T
        n: Batch size (must be at least 1)
        strict: If True, raises ValueError if the last batch is incomplete

    Returns:
        Iterator yielding lists of items from the input iterable

    Raises:
        ValueError: If n < 1 or if strict=True and last batch is incomplete
    """
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := list(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch
