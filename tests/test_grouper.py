# -*- coding: utf-8 -*-

from s3manifesto.grouper import group_files

import math
import random
from s3manifesto.model import FileSpec


def test_group_files_complex_example():
    """Test the complex example from the docstring."""
    # Create files matching the docstring example
    file_values = [150, 120, 80, 75, 60, 50, 45, 40, 30, 25, 20, 15, 10, 5]
    file_specs = [
        FileSpec(uri=f"file-{i}", value=value) for i, value in enumerate(file_values)
    ]

    group_specs = group_files(file_specs, target_value=100)

    # Verify the expected grouping from docstring
    expected_groups = [
        [150],  # Oversized file
        [120],  # Oversized file
        [80, 20],  # 100 total
        [75, 25],  # 100 total
        [60, 40],  # 100 total
        [50, 45, 5],  # 100 total
        [30, 15, 10],  # 55 total (remaining)
    ]

    assert len(group_specs) == len(
        expected_groups
    ), f"Expected {len(expected_groups)} groups, got {len(group_specs)}"
    for i, (group_spec, expected_values) in enumerate(
        zip(group_specs, expected_groups)
    ):
        actual_values = [file_spec.value for file_spec in group_spec.file_specs]
        actual_total = sum(actual_values)
        expected_total = sum(expected_values)

        # Check that group total matches expected
        assert (
            actual_total == expected_total
        ), f"Group {i}: expected total {expected_total}, got {actual_total}"
        assert group_spec.value == actual_total, f"Group {i}: GroupSpec.value mismatch"

        # Check that no group exceeds target (except oversized files)
        if expected_total <= 100:
            assert (
                actual_total <= 100
            ), f"Group {i} exceeds target: {actual_total} > 100"

        # print(f"Group {i}: {actual_values} = {actual_total}")  # for debug only


def _test_group_files_using_random_data(
    n_small_items: int = 80,
    n_large_items: int = 20,
    small_item_min_value: int = 1,
    small_item_max_value: int = 100,
    large_item_min_value: int = 90,
    large_item_max_value: int = 300,
    target_value: int = 100,
    verbose: bool = False,
):
    file_specs = list()
    i = 0
    for _ in range(n_small_items):
        i += 1
        file_specs.append(
            FileSpec(
                uri=f"small-{i}",
                value=random.randint(small_item_min_value, small_item_max_value),
            )
        )
    for _ in range(n_large_items):
        i += 1
        file_specs.append(
            FileSpec(
                uri=f"large-{i}",
                value=random.randint(large_item_min_value, large_item_max_value),
            )
        )

    group_specs = group_files(file_specs, target_value=target_value)

    total_value = sum([file_spec.value for file_spec in file_specs])
    actual_value = sum(
        [
            target_value if group_spec.value <= target_value else group_spec.value
            for group_spec in group_specs
        ]
    )
    utilization = total_value / actual_value
    utilization = float(f"{utilization*100:.2f}")

    sorted_group_specs = sorted(
        group_specs, key=lambda group_spec: group_spec.value, reverse=True
    )
    best_n_group = 0
    remaining_total_value = total_value
    for group_spec in sorted_group_specs:
        if group_spec.value > target_value:
            best_n_group += 1
            remaining_total_value -= group_spec.value
    best_n_group += math.ceil(remaining_total_value / target_value)
    actual_n_group = len(group_specs)

    numbers = [file_spec.value for file_spec in file_specs]
    numbers.sort(reverse=True)
    grouped_numbers = [
        [file_spec.value for file_spec in group_spec.file_specs]
        for group_spec in group_specs
    ]

    if verbose:
        print(f"{numbers = }")
        print(f"{grouped_numbers = }")
        print(f"{total_value = }")
        print(f"{actual_value = }")
        print(f"{utilization = }%")
        print(f"{best_n_group = }")
        print(f"{actual_n_group = }")

    assert utilization >= 90


def test_group_files_using_random_data():
    print("")
    n_test = 10
    for _ in range(n_test):
        _test_group_files_using_random_data(verbose=True)


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3manifesto.grouper",
        preview=False,
    )
