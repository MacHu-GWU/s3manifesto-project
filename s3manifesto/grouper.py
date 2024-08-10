# -*- coding: utf-8 -*-

import typing as T
from collections import deque

from .typehint import T_FILE_SPEC


def group_files(
    files: T.List[T_FILE_SPEC],
    target: int,
    sort_by_target: bool = True,
) -> T.List[T.Tuple[T.List[T_FILE_SPEC], int]]:
    """
    Given a list of :class:`File` and a target size, put them into groups,
    so that each group has approximately the same size as the target size.

    :param files: List of files to be grouped
    :param target: Target size or target n_record for each group
    """
    half_target_size = target // 2

    if sort_by_target:
        files = deque(sorted(files, key=lambda x: [1]))
    else:  # pragma: no cover
        files = deque(files)

    file_groups = list()
    file_group = list()
    file_group_size = 0

    while 1:
        # if no files left
        if len(files) == 0:
            if len(file_group):
                file_groups.append((file_group, file_group_size))
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
            file_groups.append((file_group, file_group_size))
            file_group = list()
            file_group_size = 0

    return file_groups
