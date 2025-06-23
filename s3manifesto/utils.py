# -*- coding: utf-8 -*-

import typing as T
import io

import polars as pl

from .typehint import T_RECORD


def write_parquet(records: T.List[T_RECORD]) -> bytes:
    df = pl.DataFrame(records)
    buffer = io.BytesIO()
    df.write_parquet(buffer, compression="snappy")
    return buffer.getvalue()


def read_parquet(b: bytes) -> T.List[T_RECORD]:
    df = pl.read_parquet(b)
    return df.to_dicts()


def split_s3_uri(uri: str) -> T.Tuple[str, str]:
    parts = uri.split("/", 3)
    bucket = parts[2]
    key = parts[3]
    return bucket, key


def human_size(n: int) -> str:
    if n < 1024:
        return f"{n} B"

    size = float(n)
    for unit in ["KB", "MB", "GB", "TB", "PB", "EB"]:
        size /= 1024.0
        if size < 1024:
            return f"{size:.2f} {unit}"
    return f"{size:.2f} EB"
