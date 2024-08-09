# -*- coding: utf-8 -*-

"""
Benchmark result::

.. code-block:: python

    n_records = 1000000
    {
        "Write ndjson": 1.875375,
        "Read ndjson": 0.356473,
        "Write parquet": 0.25004,
        "Read parquet": 0.288895
    }
"""

import typing as T
import io
import gzip
import json
import random

import polars as pl

from s3manifesto.vendor.timer import DateTimeTimer


T_RECORD = T.Dict[str, T.Any]


def write_ndjson(records: T.List[T_RECORD]) -> bytes:
    df = pl.DataFrame(records)
    buffer = io.BytesIO()
    df.write_ndjson(buffer)
    return gzip.compress(buffer.getvalue())


def read_ndjson(b: bytes) -> T.List[T_RECORD]:
    df = pl.read_ndjson(gzip.decompress(b))
    return df.to_dicts()


def write_parquet(records: T.List[T_RECORD]) -> bytes:
    df = pl.DataFrame(records)
    buffer = io.BytesIO()
    # df.write_parquet(buffer, compression="snappy")
    df.write_parquet(buffer, compression="zstd", pyarrow_options={"use_dictionary": True})
    return buffer.getvalue()


def read_parquet(b: bytes) -> T.List[T_RECORD]:
    df = pl.read_parquet(b)
    return df.to_dicts()


def test_performance():
    # n_records = 1_000
    # n_records = 10_000
    # n_records = 100_000
    n_records = 1_000_000
    # n_records = 10_000_000

    prefix = "s3://mybucket/data"
    records = [
        {
            "prefix": prefix,
            "file": f"{ith}.parquet",
            "size": random.randint(1000 * 1000, 10 * 1000 * 1000),
        }
        for ith in range(1, 1 + n_records)
    ]

    display = True
    # display = False

    result = {}

    # with DateTimeTimer("Write ndjson", display=display) as timer:
    #     b1 = write_ndjson(records)
    # result["Write ndjson"] = timer.elapsed
    # size1 = len(b1)
    #
    # with DateTimeTimer("Read ndjson", display=display) as timer:
    #     records1 = read_ndjson(b1)
    # result["Read ndjson"] = timer.elapsed
    # assert len(records1) == n_records
    # if n_records <= 1000:
    #     assert records1 == records

    with DateTimeTimer("Write parquet", display=display) as timer:
        b2 = write_parquet(records)
    result["Write parquet"] = timer.elapsed
    size2 = len(b2)

    with DateTimeTimer("Read parquet", display=display) as timer:
        records2 = read_parquet(b2)
    result["Read parquet"] = timer.elapsed
    assert len(records2) == n_records
    if n_records <= 1000:
        assert records2 == records

    if display:
        print(f"{n_records = }")
        print(json.dumps(result, indent=4))


test_performance()
