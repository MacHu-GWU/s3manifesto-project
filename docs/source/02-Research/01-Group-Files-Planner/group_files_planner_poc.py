# -*- coding: utf-8 -*-

"""
Benchmark::

    ========== V1 ==========
    V1: from 2024-08-09 00:15:16.634320 to 2024-08-09 00:15:17.065350 elapsed 0.431030 second.
    n_group = 313702, n_file = 1000000
    186 [30, 2, 84, 70]
    207 [77, 37, 93]
    137 [51, 86]
    135 [87, 48]
    178 [41, 68, 69]
    ========== V2 ==========
    V2: from 2024-08-09 00:15:17.074063 to 2024-08-09 00:15:18.011648 elapsed 0.937585 second.
    n_group = 394647, n_file = 1000000
    116 [30, 2, 84]
    70 [70]
    114 [77, 37]
    144 [93, 51]
    173 [86, 87]
    {'elapse1': 0.43103, 'elapse2': 0.937585}
"""

import typing as T
from collections import deque

import numpy as np
import polars as pl
from rich import print as rprint

from s3manifesto.vendor.timer import DateTimeTimer

T_FILE_SPEC = T.Tuple[T.Union[str, int], int]


def calculate_group_file_plan_v1(
    files: T.List[T_FILE_SPEC],
    target: int,
) -> T.List[T.List[T_FILE_SPEC]]:
    """
    Given a list of :class:`File` and a target size, put them into groups,
    so that each group has approximately the same size as the target size.

    Pure Python implementation.
    """
    half_target_size = target // 2

    files = deque(sorted(files, key=lambda x: [1]))
    file_groups = list()
    file_group = list()
    file_group_size = 0

    while 1:
        # if no files left
        if len(files) == 0:
            if len(file_group):
                file_groups.append(file_group)
            break

        remaining_size = half_target_size - file_group_size
        # take the largest file
        if remaining_size <= half_target_size:
            file = files.popleft()
        # take the smallest file
        else:
            file = files.pop()

        file_group.append(file)
        file_group_size += file[1]

        if file_group_size >= target:
            file_groups.append(file_group)
            file_group = list()
            file_group_size = 0

    return file_groups


def calculate_group_file_plan_v2(
    df: pl.DataFrame,
    size_col: str,
    target: int,
) -> T.List[T.List[T_FILE_SPEC]]:
    """
    Polars implementation.
    """
    df = df.with_columns(pl.col(size_col).cum_sum().alias("cum_sum"))
    df = df.with_columns(
        ((pl.col("cum_sum") - pl.lit(1)) // target).alias("batch_group")
    )
    df = df.drop("cum_sum")
    file_group_list = list()
    for sub_df in df.partition_by("batch_group", include_key=False):
        sub_df["size"].sum()
        file_group_list.append(sub_df.rows())
    return file_group_list


if __name__ == "__main__":
    # n_row = 1000
    # n_row = 10_000
    # n_row = 100_000
    n_row = 1_000_000
    # n_row = 10_000_000
    lower = 1
    upper = 100
    max_sum = 128

    df = pl.DataFrame(
        {
            "id": np.arange(1, 1 + n_row),
            "size": np.random.randint(lower, upper + 1, n_row),
        }
    )
    files = df.rows()
    print("========== V1 ==========")
    with DateTimeTimer("V1") as timer:
        file_group_list1 = calculate_group_file_plan_v1(
            files=files,
            target=max_sum,
        )
    elapse1 = timer.elapsed

    n_group = len(file_group_list1)
    n_file = sum(len(group) for group in file_group_list1)
    print(f"n_group = {n_group}, n_file = {n_file}")
    for file_group in file_group_list1[:5]:
        size_list = [file[1] for file in file_group]
        total_size = sum(size_list)
        print(total_size, size_list)

    print("========== V2 ==========")
    with DateTimeTimer("V2") as timer:
        file_group_list2 = calculate_group_file_plan_v2(
            df=df,
            size_col="size",
            target=max_sum,
        )
    elapse2 = timer.elapsed

    n_group = len(file_group_list2)
    n_file = sum(len(group) for group in file_group_list2)
    print(f"n_group = {n_group}, n_file = {n_file}")
    for file_group in file_group_list2[:5]:
        size_list = [file[1] for file in file_group]
        total_size = sum(size_list)
        print(total_size, size_list)

    res = {"elapse1": elapse1, "elapse2": elapse2}
    rprint(res)
