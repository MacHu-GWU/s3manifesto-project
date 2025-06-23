# -*- coding: utf-8 -*-

"""
Data model classes.
"""

import dataclasses
from functools import cached_property

import polars as pl

from .compact import T
from .typehint import T_RECORD
from .utils import human_size


@dataclasses.dataclass(frozen=True)
class Base:
    """
    Base class providing common functionality for all data model classes.

    Enables efficient serialization and deserialization for distributed processing
    where task definitions need to be passed between workers and coordinators.
    """

    def to_dict(self) -> T_RECORD:  # pragma: no cover
        """
        Convert the dataclass instance to a dictionary.

        Returns:
            A dictionary representation of the dataclass instance.
        """
        return dataclasses.asdict(self)


@dataclasses.dataclass(frozen=True)
class FileSpec(Base):
    """
    Lightweight file specification containing URI and a numeric value for grouping.

    Essential for divide-and-conquer algorithms that need to partition files by size
    or record count without loading full metadata, enabling efficient task distribution.

    :param uri: Unique identifier for the file location
    :param value: Numeric value used for grouping (size in bytes or record count)
    """

    uri: str = dataclasses.field()
    value: int = dataclasses.field()

    @property
    def size_for_human(self) -> str:  # pragma: no cover
        return human_size(self.value)


@dataclasses.dataclass(frozen=True)
class GroupSpec(Base):
    """
    Represents a balanced group of files with their collective value for optimal task sizing.

    Critical for divide-and-conquer processing where work must be distributed evenly across
    parallel workers, ensuring consistent resource utilization and predictable execution times.

    :param file_specs: List of :class:`FileSpec` grouped together
    :param value: Total combined value of all files in this group
    """

    file_specs: T.List[FileSpec] = dataclasses.field()
    value: int = dataclasses.field()

    @property
    def size_for_human(self) -> str:  # pragma: no cover
        return human_size(self.value)


@dataclasses.dataclass(frozen=True)
class DataFile(Base):
    """
    Complete metadata specification for a data file including integrity and size information.

    Enables divide-and-conquer workflows to make informed decisions about task partitioning
    while providing data integrity verification through ETags for reliable distributed processing.

    :param uri: Unique S3 URI or file path identifier
    :param etag: AWS S3 ETag for data integrity verification
    :param size: File size in bytes for resource planning
    :param n_record: Number of records for workload estimation
    """

    uri: str = dataclasses.field()
    etag: T.Optional[str] = dataclasses.field(default=None)
    size: T.Optional[int] = dataclasses.field(default=None)
    n_record: T.Optional[int] = dataclasses.field(default=None)

    @property
    def size_for_human(self) -> str:  # pragma: no cover
        return human_size(self.size) if self.size is not None else "Unknown"

    @classmethod
    def dump_many_to_dataframe(cls, data_files: T.Iterable[T.Self]) -> pl.DataFrame:
        """
        Convert a list of DataFile objects to a Polars DataFrame.

        :param data_files: An iterable of :class:`DataFile` objects.

        :returns: A Polars DataFrame containing the data from the :class:`DataFile` objects.
        """
        return pl.DataFrame([dataclasses.asdict(data_file) for data_file in data_files])

    @classmethod
    def load_many_from_dataframe(cls, df: pl.DataFrame) -> T.List[T.Self]:
        """
        Convert a Polars DataFrame to a list of :class:`DataFile` objects.

        :param df: A Polars DataFrame containing the data.

        :returns: A list of :class:`DataFile` objects created from the DataFrame.
        """
        fields = dataclasses.fields(cls)
        names = {field.name for field in fields}
        wanted_cols = list()
        for col in df.columns:
            if col in names:
                wanted_cols.append(col)
        return [cls(**row) for row in df.select(wanted_cols).to_dicts()]


@dataclasses.dataclass(frozen=True)
class DataFileGroup(Base):
    """
    A collection of :class:`DataFile` grouped together for optimal parallel processing.

    Facilitates divide-and-conquer strategies by providing ready-to-execute task units
    where each group represents a balanced workload for distributed worker nodes.

    :param data_files: List of DataFile objects that should be processed together
    :param value: Total aggregated value (size or record count) for the entire group
    """

    data_files: T.List[DataFile] = dataclasses.field()
    attr_name: str = dataclasses.field()
    value: int = dataclasses.field()

    @property
    def size_for_human(self) -> str:  # pragma: no cover
        return human_size(self.value)


@dataclasses.dataclass(frozen=True)
class ManifestSummary(Base):
    """
    Compact summary metadata for a manifest file providing quick access to aggregate statistics.

    Enables divide-and-conquer coordinators to make informed decisions about task distribution
    without loading the full manifest data, optimizing planning overhead in large-scale processing.

    :param manifest: URI reference to the associated manifest data file
    :param size: Total aggregate size in bytes of all files in the manifest
    :param n_record: Total aggregate record count across all files in the manifest
    :param fingerprint: Unique hash for detecting data changes and cache invalidation
    :param details: Additional metadata for workflow-specific information
    """
    manifest: str = dataclasses.field()
    size: T.Optional[int] = dataclasses.field(default=None)
    n_record: T.Optional[int] = dataclasses.field(default=None)
    fingerprint: T.Optional[str] = dataclasses.field(default=None)
    details: T_RECORD = dataclasses.field(default_factory=dict)

    @cached_property
    def size_for_human(self) -> str:  # pragma: no cover
        return human_size(self.size) if self.size is not None else "Unknown"
