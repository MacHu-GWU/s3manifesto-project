# -*- coding: utf-8 -*-

import typing as T
import dataclasses


@dataclasses.dataclass
class FileSpec:
    uri: str
    value: int


@dataclasses.dataclass
class GroupSpec:
    file_specs: T.List[FileSpec]
    value: int


@dataclasses.dataclass(frozen=True, slots=True)
class DataFile:
    uri: str = dataclasses.field()
    etag: T.Optional[str] = dataclasses.field(default=None)
    size: T.Optional[int] = dataclasses.field(default=None)
    n_record: T.Optional[int] = dataclasses.field(default=None)
