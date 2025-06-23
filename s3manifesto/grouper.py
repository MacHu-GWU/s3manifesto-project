# -*- coding: utf-8 -*-

"""
File Grouping Algorithm for ETL Pipeline Optimization
"""

import typing as T
from collections import deque

from .typehint import T_RECORD
from .model import FileSpec, GroupSpec, DataFile


def group_files(
    file_specs: T.List[FileSpec],
    target_value: int,
    sort_by_target: bool = True,
) -> T.List[GroupSpec]:
    """
    Given a list of :class:`~s3pathlib.model.FileSpec` and a target total spec value,
    put them into groups of :class:`~s3pathlib.model.GroupSpec`,
    so that each group has approximately the same size as the target size.

    The grouping algorithm uses a deque-based approach that alternates between selecting
    the largest and smallest remaining files to create approximately equal-sized batches.
    This balancing strategy prevents scenarios where some workers finish much earlier
    than others, maximizing overall throughput in distributed processing environments.

    :param files: List of files to be grouped
    :param target: Target size or target n_record for each group
    :param sort_by_target: If True, sort files by their value before grouping
    """
    half_target_size = target_value // 2

    if sort_by_target:
        file_specs = deque(sorted(file_specs, key=lambda file: file.value))
    else:  # pragma: no cover
        file_specs = deque(file_specs)

    group_specs = list()
    sub_file_specs = list()
    group_spec_value = 0

    while 1:
        # if no files left
        if len(file_specs) == 0:
            if len(sub_file_specs):
                group_spec = GroupSpec(
                    file_specs=sub_file_specs,
                    value=group_spec_value,
                )
                group_specs.append(group_spec)
            break

        remaining_size = half_target_size - group_spec_value
        # take the largest file
        if remaining_size <= half_target_size:
            file_spec = file_specs.popleft()
        # take the smallest file
        else:
            file_spec = file_specs.pop()

        sub_file_specs.append(file_spec)
        group_spec_value += file_spec.value

        if group_spec_value >= target_value:
            group_spec = GroupSpec(
                file_specs=sub_file_specs,
                value=group_spec_value,
            )
            group_specs.append(group_spec)
            sub_file_specs = list()
            group_spec_value = 0

    return group_specs
