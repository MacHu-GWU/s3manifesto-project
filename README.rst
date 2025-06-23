
.. image:: https://readthedocs.org/projects/s3manifesto/badge/?version=latest
    :target: https://s3manifesto.readthedocs.io/en/latest/
    :alt: Documentation Status

.. image:: https://github.com/MacHu-GWU/s3manifesto-project/actions/workflows/main.yml/badge.svg
    :target: https://github.com/MacHu-GWU/s3manifesto-project/actions?query=workflow:CI

.. image:: https://codecov.io/gh/MacHu-GWU/s3manifesto-project/branch/main/graph/badge.svg
    :target: https://codecov.io/gh/MacHu-GWU/s3manifesto-project

.. image:: https://img.shields.io/pypi/v/s3manifesto.svg
    :target: https://pypi.python.org/pypi/s3manifesto

.. image:: https://img.shields.io/pypi/l/s3manifesto.svg
    :target: https://pypi.python.org/pypi/s3manifesto

.. image:: https://img.shields.io/pypi/pyversions/s3manifesto.svg
    :target: https://pypi.python.org/pypi/s3manifesto

.. image:: https://img.shields.io/badge/✍️_Release_History!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/s3manifesto-project/blob/main/release-history.rst

.. image:: https://img.shields.io/badge/⭐_Star_me_on_GitHub!--None.svg?style=social&logo=github
    :target: https://github.com/MacHu-GWU/s3manifesto-project

------

.. image:: https://img.shields.io/badge/Link-API-blue.svg
    :target: https://s3manifesto.readthedocs.io/en/latest/py-modindex.html

.. image:: https://img.shields.io/badge/Link-Install-blue.svg
    :target: `install`_

.. image:: https://img.shields.io/badge/Link-GitHub-blue.svg
    :target: https://github.com/MacHu-GWU/s3manifesto-project

.. image:: https://img.shields.io/badge/Link-Submit_Issue-blue.svg
    :target: https://github.com/MacHu-GWU/s3manifesto-project/issues

.. image:: https://img.shields.io/badge/Link-Request_Feature-blue.svg
    :target: https://github.com/MacHu-GWU/s3manifesto-project/issues

.. image:: https://img.shields.io/badge/Link-Download-blue.svg
    :target: https://pypi.org/pypi/s3manifesto#files


Welcome to ``s3manifesto`` Documentation
==============================================================================
.. image:: https://s3manifesto.readthedocs.io/en/latest/_static/s3manifesto-logo.png
    :target: https://s3manifesto.readthedocs.io/en/latest/

**Efficient file metadata management and intelligent partitioning for large-scale data processing on AWS S3.**


Why s3manifesto?
------------------------------------------------------------------------------
In big data and ETL pipelines, efficiently managing thousands or millions of files becomes a critical bottleneck. s3manifesto solves this by providing:

- **Metadata Organization**: Consolidate file metadata (URI, size, record count, ETag) into easily manageable collections
- **Intelligent Partitioning**: Automatically group files into balanced batches for optimal parallel processing
- **Divide-and-Conquer Optimization**: Implement efficient distributed processing workflows with predictable resource utilization

Instead of dealing with individual file metadata scattered across your data lake, s3manifesto enables you to treat collections of files as single, manageable units with powerful partitioning capabilities.


Core Concepts
------------------------------------------------------------------------------
**1. Manifest as Metadata Collection**

A manifest represents metadata for a collection of data files, where each data file contains:

- **S3 URI**: File location identifier
- **ETag**: Data integrity verification hash  
- **Size**: File size in bytes for resource planning
- **Record Count**: Number of records for workload estimation
- **Additional attributes**: Extensible metadata as needed

**2. Two-File Storage System**

Each manifest consists of two files stored in S3:

- **Manifest Summary File** (JSON): Aggregate statistics and references
- **Manifest Data File** (Parquet): Detailed per-file metadata in parquet format

This design enables quick access to summary information without loading detailed metadata, optimizing both storage and retrieval performance.

**3. Intelligent File Partitioning**

Manifest files can partition large collections into balanced groups using the Best Fit Decreasing (BFD) algorithm:

- **By Total Size**: Group files into batches of ~100MB each for memory optimization
- **By Record Count**: Group files into batches of ~10M records each for processing time consistency
- **Optimal Distribution**: Ensures balanced workloads across parallel workers
- **Divide-and-Conquer Ready**: Perfect for distributed processing frameworks

**Example**: Transform 10,000 files into 50 balanced groups of ~200 files each, with each group totaling approximately your target size or record count.


Quick Example
------------------------------------------------------------------------------
.. code-block:: python

    from s3manifesto import ManifestFile, DataFile
    
    # Create manifest from file metadata
    data_files = [
        DataFile(uri="s3://bucket/file1.json", size=1000000, n_record=1000, etag="abc123"),
        DataFile(uri="s3://bucket/file2.json", size=2000000, n_record=2000, etag="def456"),
        DataFile(uri="s3://bucket/file3.json", size=3000000, n_record=3000, etag="ghi789")
    ]
    
    manifest = ManifestFile.new(
        uri="s3://bucket/manifest-data.parquet",
        uri_summary="s3://bucket/manifest-summary.json", 
        data_file_list=data_files
    )
    
    # Write to S3
    manifest.write(s3_client)
    
    # Read from S3
    manifest = ManifestFile.read("s3://bucket/manifest-summary.json", s3_client)
    
    # Partition files for parallel processing
    groups = manifest.partition_files_by_size(target_size=100_000_000)  # 100MB groups
    groups = manifest.partition_files_by_n_record(target_n_record=10_000_000)  # 10M record groups


.. _install:

Install
------------------------------------------------------------------------------

``s3manifesto`` is released on PyPI, so all you need is to:

.. code-block:: console

    $ pip install s3manifesto

To upgrade to latest version:

.. code-block:: console

    $ pip install --upgrade s3manifesto
