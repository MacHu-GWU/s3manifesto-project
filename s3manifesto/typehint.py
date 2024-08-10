# -*- coding: utf-8 -*-

try:
    import typing_extensions as T
except ImportError: # pragma: no cover
    import typing as T

T_RECORD = T.Dict[str, T.Any]
# first element is the unique identifier of the file
# second element could be size of the file or the number of records in the file
T_FILE_SPEC = T.Tuple[str, int]


class T_DATA_FILE(T.TypedDict):
    uri: T.Required[str]
    etag: T.Required[T.Optional[str]]
    size: T.Required[T.Optional[int]]
    n_record: T.Required[T.Optional[int]]
