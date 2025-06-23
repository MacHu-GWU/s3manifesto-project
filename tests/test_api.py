# -*- coding: utf-8 -*-

from s3manifesto import api


def test():
    _ = api
    _ = api.T_RECORD
    _ = api.KeyEnum
    _ = api.FileSpec
    _ = api.GroupSpec
    _ = api.DataFile
    _ = api.DataFileGroup
    _ = api.ManifestSummary
    _ = api.group_files
    _ = api.ManifestFile
    _ = api.ManifestFile.partition_files_by_size
    _ = api.ManifestFile.partition_files_by_n_record


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3manifesto.api",
        preview=False,
    )
