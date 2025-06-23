# -*- coding: utf-8 -*-

from s3manifesto.model import (
    FileSpec,
    GroupSpec,
    DataFile,
    DataFileGroup,
    ManifestSummary,
)

import polars as pl
from s3manifesto.constants import KeyEnum


class TestDataFile:
    def test_batch_read_write(self):
        data_file = DataFile(uri="s3://bucket/1.json")
        df = DataFile.dump_many_to_dataframe([data_file])
        # print(df) # for debug only
        data_file_1 = DataFile.load_many_from_dataframe(df)[0]
        # print(data_file_1)  # for debug only

        df = pl.DataFrame({KeyEnum.URI: ["s3://bucket/1.json"], "invalid": [1]})
        data_file = DataFile.load_many_from_dataframe(df)[0]
        # print(data_file)  # for debug only
        assert data_file.uri == "s3://bucket/1.json"


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3manifesto.model",
        preview=False,
    )
