# -*- coding: utf-8 -*-

from s3manifesto import api


def test():
    _ = api
    _ = api.T_RECORD
    _ = api.T_FILE_SPEC
    _ = api.T_DATA_FILE
    _ = api.KeyEnum
    _ = api.group_files
    _ = api.ManifestFile


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(__file__, "s3manifesto.api", preview=False)
