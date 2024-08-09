# -*- coding: utf-8 -*-

import random

from s3manifesto.grouper import group_files


def test_group_files():
    files = list()
    i = 0
    for _ in range(1, 90):
        i += 1
        files.append((f"f-{i}", random.randint(1, 5)))
    for _ in range(10):
        i += 1
        files.append((f"f-{i}", random.randint(50, 100)))
    file_groups = group_files(files, target=64)
    for file_group in file_groups:
        size_list = [file[1] for file in file_group]
        total_size = sum(size_list)
        # print(total_size, size_list)

    files = list()
    i = 0
    for _ in range(1, 100):
        i += 1
        files.append((f"f-{i}", random.randint(32, 128)))
    file_groups = group_files(files, target=64)
    for file_group in file_groups:
        size_list = [file[1] for file in file_group]
        total_size = sum(size_list)
        # print(total_size, size_list)


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(__file__, "s3manifesto.grouper", preview=False)
