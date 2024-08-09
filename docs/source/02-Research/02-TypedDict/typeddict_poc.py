# -*- coding: utf-8 -*-

"""
在处理大量 (百万级以上) 数据文件的 metadata 时无论使用 dataclasses, attrs 还是 pydantic
都会有额外的性能开销. 因为我的数据是可信的, 我不需要序列化和反序列化以及 validation 这些功能.
所以我希望用 TypedDict 来替代这些库. 该脚本测试了这一做法的可行性.
"""

import typing_extensions as T


class T_DATA_FILE(T.TypedDict):
    uri: T.Required[str]
    size: T.Required[T.Optional[int]]
    n_record: T.Required[T.Optional[int]]
    format: T.NotRequired[T.Optional[str]]


def func(data_file: T_DATA_FILE):
    pass


# fmt: off
_ = func({"id": 1})
_ = func({"uri": "s3://bucket/key"})
_ = func({"uri": "s3://bucket/key", "size": 1, "n_record": 1})
_ = func({"uri": "s3://bucket/key", "size": None, "n_record": None})
_ = func({"uri": "s3://bucket/key", "size": 1, "n_record": 1, "format": "csv"})
_ = func({"uri": "s3://bucket/key", "size": 1, "n_record": 1, "format": "csv", "compression": "gzip"})
# fmt: on
