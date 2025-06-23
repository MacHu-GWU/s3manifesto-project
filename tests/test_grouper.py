# -*- coding: utf-8 -*-

from s3manifesto.grouper import group_files

import random
from s3manifesto.model import FileSpec


def test_group_files():
    file_specs = list()
    i = 0
    for _ in range(1, 90):
        i += 1
        file_spec = FileSpec(uri=f"f-{i}", value=random.randint(1, 5))
        file_specs.append(file_spec)
    for _ in range(10):
        i += 1
        file_spec = FileSpec(uri=f"f-{i}", value=random.randint(50, 100))
        file_specs.append(file_spec)
    group_specs = group_files(file_specs, target_value=64)
    for group_spec in group_specs:
        size_list = [file_spec.value for file_spec in group_spec.file_specs]
        total_size = sum(size_list)
        print(total_size, group_spec.value, size_list)  # for debug only

    # files = list()
    # i = 0
    # for _ in range(1, 100):
    #     i += 1
    #     files.append((f"f-{i}", random.randint(32, 128)))
    # file_groups = group_files(files, target=64)
    # for file_group, file_group_size in file_groups:
    #     size_list = [file[1] for file in file_group]
    #     total_size = sum(size_list)
    #     # print(total_size, file_group_size, size_list)


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3manifesto.grouper",
        preview=False,
    )
