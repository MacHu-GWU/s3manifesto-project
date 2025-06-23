# -*- coding: utf-8 -*-

from s3manifesto.utils import (
    read_parquet,
    write_parquet,
    split_s3_uri,
)

import polars as pl


def test_read_and_write_parquet():
    records = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    b = write_parquet(records)
    records_1 = read_parquet(b)
    print(records_1)


def test_split_s3_uri():
    uri = "s3://my-bucket/path/to/file.txt"
    bucket, key = split_s3_uri(uri)
    assert bucket == "my-bucket"
    assert key == "path/to/file.txt"


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3manifesto.utils",
        preview=False,
    )
