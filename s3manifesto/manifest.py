# -*- coding: utf-8 -*-

"""
In ETL (Extract, Transform, Load) pipelines, it's a common practice to group
numerous files into appropriately sized batches, each forming a distinct task.
This approach optimizes processing efficiency and resource utilization.

However, this method reqiures an effective mechanism for storing and
retrieving metadata. Ideally, we should be able to access the metadata for
an entire task in a single operation, eliminating the need to read each file
individually. This approach significantly reduces I/O operations and improves
overall performance.

This module implements an abstraction layer to achieve this functionality.
It provides a streamlined interface for grouping files, managing their associated
metadata, and enabling efficient batch processing in ETL workflows.
"""

import typing as T
import io
import json
import hashlib
import dataclasses
from functools import cached_property

import polars as pl

from .typehint import T_RECORD, T_DATA_FILE
from .constants import KeyEnum
from .grouper import group_files


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


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


@dataclasses.dataclass
class ManifestFile:
    """
    Manifest file refers to two files:

    - Manifest file: Contains the metadata of the data files. It is a parquet file
        that contains the metadata of the data files. Each row in the parquet file
        is a

    :param uri: URI of the manifest file.
    :param uri_summary: URI of the manifest summary file.
    :param data_file_list: List of data files.
    :param size: Total size of the data files.
    :param n_record: Total number of records in the data files.
    """

    uri: str = dataclasses.field()
    uri_summary: str = dataclasses.field()
    data_file_list: T.List[T_DATA_FILE] = dataclasses.field(default_factory=list)
    size: T.Optional[int] = dataclasses.field(default=None)
    n_record: T.Optional[int] = dataclasses.field(default=None)

    def calculate(self):
        size_list = list()
        n_record_list = list()
        SIZE = KeyEnum.SIZE
        N_RECORD = KeyEnum.N_RECORD

        if (self.size is None) and (self.n_record is None):
            for data_file in self.data_file_list:
                size_list.append(data_file[SIZE])
                n_record_list.append(data_file[N_RECORD])
        elif self.size is None:  # pragma: no cover
            for data_file in self.data_file_list:
                size_list.append(data_file[SIZE])
        elif self.n_record is None:  # pragma: no cover
            for data_file in self.data_file_list:
                n_record_list.append(data_file[N_RECORD])
        else:  # pragma: no cover
            pass

        try:
            if size_list:
                size = sum(size_list)
                self.size = size
        except:  # pragma: no cover
            pass

        try:
            if n_record_list:
                n_record = sum(n_record_list)
                self.n_record = n_record
        except:  # pragma: no cover
            pass

    @classmethod
    def new(
        cls,
        uri: str,
        uri_summary: str,
        data_file_list: T.List[T_DATA_FILE],
        size: T.Optional[int] = None,
        n_record: T.Optional[int] = None,
        calculate: bool = True,
    ):
        manifest_file = cls(
            uri=uri,
            uri_summary=uri_summary,
            data_file_list=data_file_list,
            size=size,
            n_record=n_record,
        )
        if calculate:
            manifest_file.calculate()
        return manifest_file

    def write(
        self,
        s3_client: "S3Client",
    ):
        """
        Write the manifest file to S3.
        """
        manifest_summary = {
            KeyEnum.MANIFEST: self.uri,
            KeyEnum.SIZE: self.size,
            KeyEnum.N_RECORD: self.n_record,
        }
        bucket, key = split_s3_uri(self.uri_summary)
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(manifest_summary, indent=4),
            ContentType="application/json",
        )
        bucket, key = split_s3_uri(self.uri)
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=write_parquet(self.data_file_list),
            ContentType="application/octet-stream",
            ContentEncoding="gzip",
        )

    @classmethod
    def read(cls, uri_summary: str, s3_client: "S3Client"):
        """
        Read the manifest file from S3.
        """
        bucket, key = split_s3_uri(uri_summary)
        res = s3_client.get_object(Bucket=bucket, Key=key)
        dct = json.loads(res["Body"].read().decode("utf-8"))

        bucket, key = split_s3_uri(dct[KeyEnum.MANIFEST])
        res = s3_client.get_object(Bucket=bucket, Key=key)
        data_file_list = read_parquet(res["Body"].read())
        manifest_file = cls.new(
            uri=dct[KeyEnum.MANIFEST],
            uri_summary=uri_summary,
            size=dct[KeyEnum.SIZE],
            n_record=dct[KeyEnum.N_RECORD],
            data_file_list=data_file_list,
            calculate=False,
        )
        return manifest_file

    @cached_property
    def fingerprint(self) -> str:
        """
        A unique fingerprint for the manifest file. It is calculated based on
        the URI and ETag of the data files.
        """
        md5 = hashlib.md5()
        for data_file in sorted(self.data_file_list, key=lambda x: x[KeyEnum.URI]):
            md5.update(data_file[KeyEnum.URI].encode("utf-8"))
            md5.update(data_file[KeyEnum.ETAG].encode("utf-8"))
        return md5.hexdigest()

    def _group_files_into_tasks(
        self,
        attr_name: str,
        target: int = 100 * 1000 * 1000,  ## 100 MB
    ) -> T.List[T.List["T_DATA_FILE"]]:
        """
        Group the snapshot data files into tasks.
        """
        URI = KeyEnum.URI
        mapping = {data_file[URI]: data_file for data_file in self.data_file_list}
        files = [
            (data_file[URI], data_file[attr_name]) for data_file in self.data_file_list
        ]
        file_groups = group_files(files=files, target=target)
        data_file_group_list = list()
        for file_group in file_groups:
            data_file_list = [mapping[uri] for uri, _ in file_group]
            data_file_group_list.append(data_file_list)
        return data_file_group_list

    def group_files_into_tasks_by_size(
        self,
        target_size: int = 100 * 1000 * 1000,  ## 100 MB in size
    ) -> T.List[T.List["T_DATA_FILE"]]:
        """
        Organize data files into balanced task groups, ensuring each group's
        total file size approximates a specified target,
        optimizing workload distribution.

        :param target_size: Target size for each task group in bytes.
        """
        return self._group_files_into_tasks(
            attr_name=KeyEnum.SIZE,
            target=target_size,
        )

    def group_files_into_tasks_by_n_record(
        self,
        target_n_record: int = 10 * 1000 * 1000,  ## 10M records
    ) -> T.List[T.List["T_DATA_FILE"]]:
        """
        Organize data files into balanced task groups, ensuring each group's
        total number of records approximates a specified target,
        optimizing workload distribution.

        :param target_n_record: Target number of records for each task group.
        """
        return self._group_files_into_tasks(
            attr_name=KeyEnum.N_RECORD,
            target=target_n_record,
        )


T_MANIFEST_FILE = T.TypeVar("T_MANIFEST_FILE", bound=ManifestFile)
