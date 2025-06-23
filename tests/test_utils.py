# -*- coding: utf-8 -*-

from s3manifesto.utils import (
    read_parquet,
    write_parquet,
    split_s3_uri,
    human_size,
)


def test_read_and_write_parquet():
    records = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    b = write_parquet(records)
    records_1 = read_parquet(b)
    # print(records_1) # for debug only


def test_split_s3_uri():
    uri = "s3://my-bucket/path/to/file.txt"
    bucket, key = split_s3_uri(uri)
    assert bucket == "my-bucket"
    assert key == "path/to/file.txt"


def test_human_size():
    cases = [
        (15, "15 B"),
        (1023, "1023 B"),
        (1024, "1.00 KB"),
        (1500, "1.46 KB"),
        (2048, "2.00 KB"),
        (5_242_880, "5.00 MB"),
        (8_796_093_022, "8.19 GB"),
        (1_099_511_627_776, "1.00 TB"),
        (555_555_555_555_555_555, "493.43 PB"),
        (555_555_555_555_555_555_555, "481.87 EB"),
        (555_555_555_555_555_555_555_555, "481867.63 EB"),
    ]
    for size, expected in cases:
        size_for_human = human_size(size)
        # print(f"{size = }, {size_for_human = }, {expected = }") # for debug only
        assert size_for_human == expected


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3manifesto.utils",
        preview=False,
    )
