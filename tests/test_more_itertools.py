# -*- coding: utf-8 -*-

from s3manifesto.more_itertools import batched

import pytest
import dataclasses


@dataclasses.dataclass
class User:
    id: int

    def user_method(self):
        pass


def test_batched():
    users = [User(id=1), User(id=2), User(id=3)]

    for sub_users in batched(users, 2):
        for user in sub_users:
            user.user_method()  # type hint works

    with pytest.raises(ValueError):
        list(batched(users, -1))

    with pytest.raises(ValueError):
        list(batched(users, 2, strict=True))


if __name__ == "__main__":
    from s3manifesto.tests import run_cov_test

    run_cov_test(
        __file__,
        "s3manifesto.more_itertools",
        preview=False,
    )
