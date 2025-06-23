# -*- coding: utf-8 -*-

"""
Manifest file system for efficient metadata management and file grouping in ETL pipelines.

Provides the :class:`ManifestFile` class for creating, storing, and retrieving file metadata
collections, enabling optimized batch processing and intelligent file partitioning.
"""

import json
import hashlib
import dataclasses

from .compact import T
from .constants import KeyEnum
from .model import FileSpec, DataFile, DataFileGroup, ManifestSummary
from .utils import write_parquet, read_parquet, split_s3_uri, human_size
from .grouper import group_files


if T.TYPE_CHECKING:  # pragma: no cover
    from mypy_boto3_s3.client import S3Client


@dataclasses.dataclass
class ManifestFile:
    """
    Core manifest file system consisting of two linked files for efficient metadata management.

    **Manifest File Structure:**

    A complete manifest consists of two files that work together:

    1. **Manifest Summary File** (JSON): Contains aggregate metadata and references, Example::

        {
            "n_files": 50,
            "total_size": 600_000_000, # 600 MB
            "total_records": 100_000,
            "uri": "s3://bucket/prefix/manifest.parquet",
            "fingerprint": "2d0175ad9416dc5fd7138546471738ca"
        }

    2. **Manifest Data File** (Parquet): Contains detailed per-file metadata, example::

        +-------------------------------+--------------+----------+----------------------------------+
        |              uri              | size (Bytes) | n_record |               Etag               |
        +-------------------------------+--------------+----------+----------------------------------+
        | s3://bucket/prefix/file1.json |   1_000_000  |   1000   | 8a53247196e46b53699d065ba3cc8e0d |
        +-------------------------------+--------------+----------+----------------------------------+
        | s3://bucket/prefix/file2.json |   2_000_000  |   2000   | b3f20f3c7a8877c24504634edd067fcf |
        +-------------------------------+--------------+----------+----------------------------------+
        | s3://bucket/prefix/file3.json |   3_000_000  |   3000   | dd9b315f1d7ec573cb7305e6e238731f |
        +-------------------------------+--------------+----------+----------------------------------+
        |              ...              |      ...     |    ...   |                ...               |
        +-------------------------------+--------------+----------+----------------------------------+
        |              ...              |      ...     |    ...   |                ...               |
        +-------------------------------+--------------+----------+----------------------------------+
        |              ...              |      ...     |    ...   |                ...               |
        +-------------------------------+--------------+----------+----------------------------------+

    **Write Process:**

    When creating a manifest, write the Manifest Summary File first, then the Manifest
    Data File to S3, ensuring atomicity and consistency.

    **Read Process:**

    When reading a manifest, read the Manifest Summary File first to get aggregate
    statistics and the URI reference, then read the Manifest Data File for detailed metadata.

    **Simple Usage Examples:**

    Creating and writing a manifest::

        data_files = [
            DataFile(uri="s3://bucket/file1.json", size=1000000, n_record=1000, etag="abc123"),
            DataFile(uri="s3://bucket/file2.json", size=2000000, n_record=2000, etag="def456"),
            DataFile(uri="s3://bucket/file3.json", size=3000000, n_record=3000, etag="ghi789")
        ]

        manifest = ManifestFile.new(
            uri="s3://bucket/manifest-data.parquet",
            uri_summary="s3://bucket/manifest-summary.json",
            data_file_list=data_files,
        )
        manifest.write(s3_client)

    Reading a manifest::

        manifest = ManifestFile.read(
            uri_summary="s3://bucket/manifest-summary.json",
            s3_client=s3_client,
        )
        print(f"Total files: {len(manifest.data_file_list)}")
        print(f"Total size: {manifest.size} bytes")

    **File Partitioning:**

    Manifest files are essentially collections of file metadata that can be intelligently
    partitioned for parallel processing. Use :meth:`partition_files_by_size` and
    :meth:`partition_files_by_n_record` to efficiently split files into balanced groups.

    You can use :class:`ManifestFile` in two ways:
    - As a **file splitter calculator** (in-memory partitioning without S3 storage)
    - As a **persistent manifest file storage** (with S3 read/write operations)

    See the :ref:`Quick Start Guide <quick-start>` for complete examples.

    :param uri: URI of the Manifest Data File (Parquet format)
    :param uri_summary: URI of the Manifest Summary File (JSON format)
    :param data_file_list: List of DataFile objects with metadata
    :param size: Total aggregate size in bytes of all files
    :param n_record: Total aggregate record count across all files
    :param fingerprint: Unique hash for detecting data changes and cache invalidation
    :param details: Additional workflow-specific metadata
    """

    uri: str = dataclasses.field()
    uri_summary: str = dataclasses.field()
    data_file_list: T.List[DataFile] = dataclasses.field(default_factory=list)
    size: T.Optional[int] = dataclasses.field(default=None)
    n_record: T.Optional[int] = dataclasses.field(default=None)
    fingerprint: T.Optional[str] = dataclasses.field(default=None)
    details: T.Dict[str, T.Any] = dataclasses.field(default_factory=dict)

    @property
    def n_data_file(self) -> int:
        """
        Get the number of data files in the manifest.
        """
        return len(self.data_file_list)

    @property
    def size_for_human(self) -> str:  # pragma: no cover
        return human_size(self.size) if self.size is not None else "Unknown"

    def calculate(self):
        """
        Calculate total size, n_record, and fingerprint of the data files in a single pass.

        We use pre-calculated values stored as instance attributes rather than
        lazy-loaded cached properties for performance optimization. Since calculating
        size, n_record, and fingerprint all require iterating through the data_file_list,
        using separate cached properties would result in multiple for-loops (one per
        property access). This single calculate() method performs all computations
        in one pass, significantly improving efficiency for large file collections.
        """
        size_list = list()
        n_record_list = list()

        if (self.size is None) and (self.n_record is None):
            for data_file in self.data_file_list:
                size_list.append(data_file.size)
                n_record_list.append(data_file.n_record)
        elif self.size is None:  # pragma: no cover
            for data_file in self.data_file_list:
                size_list.append(data_file.size)
        elif self.n_record is None:  # pragma: no cover
            for data_file in self.data_file_list:
                n_record_list.append(data_file.n_record)
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

        try:
            md5 = hashlib.md5()
            for data_file in sorted(
                self.data_file_list, key=lambda data_file: data_file.uri
            ):
                md5.update(data_file.uri.encode("utf-8"))
                md5.update(data_file.etag.encode("utf-8"))
            self.fingerprint = md5.hexdigest()
        except:  # pragma: no cover
            pass

    @classmethod
    def new(
        cls,
        uri: str,
        uri_summary: str,
        data_file_list: T.List[DataFile],
        size: T.Optional[int] = None,
        n_record: T.Optional[int] = None,
        fingerprint: T.Optional[str] = None,
        details: T.Optional[T.Dict[str, T.Any]] = None,
        calculate: bool = True,
    ) -> T.Self:
        """
        Create a new manifest file object. To load manifest file data from S3,
        use the :meth:`read` method.

        :param uri: URI of the manifest data file.
        :param uri_summary: URI of the manifest summary file.
        :param data_file_list: List of data files.
        :param size: Total size of the data files.
        :param n_record: Total number of records in the data files.
        :param calculate: If True, calculate the size and n_record using the data_file_list.
        """
        if details is None:
            details = dict()
        manifest_file = cls(
            uri=uri,
            uri_summary=uri_summary,
            data_file_list=data_file_list,
            size=size,
            n_record=n_record,
            fingerprint=fingerprint,
            details=details,
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

        :param s3_client: boto3.client("s3") object.
        """
        manifest_summary = ManifestSummary(
            manifest=self.uri,
            size=self.size,
            n_record=self.n_record,
            fingerprint=self.fingerprint,
            details=self.details,
        )
        bucket, key = split_s3_uri(self.uri_summary)
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=json.dumps(manifest_summary.to_dict(), indent=4),
            ContentType="application/json",
        )
        bucket, key = split_s3_uri(self.uri)
        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=write_parquet(
                [data_file.to_dict() for data_file in self.data_file_list]
            ),
            ContentType="application/octet-stream",
            ContentEncoding="gzip",
        )

    @classmethod
    def read(
        cls,
        uri_summary: str,
        s3_client: "S3Client",
    ) -> T.Self:
        """
        Read the manifest file from S3.

        :param uri_summary: URI of the manifest summary file. (NOT THE MANIFEST DATA FILE)
        :param s3_client: boto3.client("s3") object.
        """
        bucket, key = split_s3_uri(uri_summary)
        res = s3_client.get_object(Bucket=bucket, Key=key)
        dct = json.loads(res["Body"].read().decode("utf-8"))
        manifest_summary = ManifestSummary(**dct)

        bucket, key = split_s3_uri(dct[KeyEnum.MANIFEST])
        res = s3_client.get_object(Bucket=bucket, Key=key)
        data_file_list = [DataFile(**dct) for dct in read_parquet(res["Body"].read())]
        manifest_file = cls.new(
            uri=manifest_summary.manifest,
            uri_summary=uri_summary,
            size=manifest_summary.size,
            n_record=manifest_summary.n_record,
            data_file_list=data_file_list,
            fingerprint=manifest_summary.fingerprint,
            details=manifest_summary.details,
            calculate=False,
        )
        return manifest_file

    def _partition_files_by_value(
        self,
        attr_name: str,
        target_value: int,
    ) -> T.List[DataFileGroup]:
        """
        Group the snapshot data files into tasks.
        """
        mapping: dict[str, DataFile] = {
            data_file.uri: data_file for data_file in self.data_file_list
        }
        file_specs = [
            FileSpec(uri=data_file.uri, value=getattr(data_file, attr_name))
            for data_file in self.data_file_list
        ]
        group_specs = group_files(file_specs=file_specs, target_value=target_value)
        groups = list()
        for group_spec in group_specs:
            group = DataFileGroup(
                data_files=[
                    mapping[file_spec.uri] for file_spec in group_spec.file_specs
                ],
                attr_name=attr_name,
                value=group_spec.value,
            )
            groups.append(group)
        return groups

    def partition_files_by_size(
        self,
        target_size: int = 100 * 1000 * 1000,  ## 100 MB in size
    ) -> T.List[DataFileGroup]:
        """
        Organize data files into balanced task groups, ensuring each group's
        total file size approximates a specified target,
        optimizing workload distribution.

        :param target_size: Target size for each task group in bytes.
        """
        return self._partition_files_by_value(
            attr_name=KeyEnum.SIZE,
            target_value=target_size,
        )

    def partition_files_by_n_record(
        self,
        target_n_record: int = 10 * 1000 * 1000,  ## 10M records
    ) -> T.List[DataFileGroup]:
        """
        Organize data files into balanced task groups, ensuring each group's
        total number of records approximates a specified target,
        optimizing workload distribution.

        :param target_n_record: Target number of records for each task group.
        """
        return self._partition_files_by_value(
            attr_name=KeyEnum.N_RECORD,
            target_value=target_n_record,
        )


T_MANIFEST_FILE = T.TypeVar("T_MANIFEST_FILE", bound=ManifestFile)
