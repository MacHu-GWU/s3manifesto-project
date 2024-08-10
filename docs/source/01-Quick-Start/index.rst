Quick Start
==============================================================================


What is a Manifest File
------------------------------------------------------------------------------
A manifest file is a specialized file format that stores metadata for a group of related files. This metadata serves as a comprehensive index, providing crucial information about each file in the group.

Key components of file metadata include:

1. **URI (Uniform Resource Identifier)**: Specifies the file's location, enabling processors to locate and read it efficiently.
2. **Size**: Indicates the file's size, typically in bytes.
3. **Record Count**: Represents the number of system records within the file. When combined with the file size, this information helps processors estimate processing time, required computational power, and memory consumption. This data is invaluable for orchestrators when scheduling processing tasks.
4. **ETag**: A cryptographic digest of the file used to verify its integrity. If a file becomes corrupted, its ETag hash will differ from the one recorded in the manifest file. Once the file is moved, copied, changed, this value will change. See https://docs.aws.amazon.com/AmazonS3/latest/API/API_Object.html for more information.

A complete "Manifest" consists of two files:

1. **Manifest Data File**: This file stores a dataframe containing metadata for all files in the group. Each row represents a single file, with columns corresponding to the metadata fields mentioned above. While various formats can be used to store this dataframe (e.g., CSV, JSON), this project utilizes the Parquet format for its exceptional I/O performance. See :ref:`ndjson-or-parquet` this section for how we made the decision to use Parquet.
2. **Manifest Summary File**: A concise JSON file that provides an overview of the entire file group. It includes aggregate information such as:
   - Total number of files
   - Combined size of all files
   - Total record count across all files
   - URI of the manifest data file, so that processor can locate it.
   - A unique fingerprint for the manifest file. It is calculated based on the URI and ETag of the data files.

This two-file structure allows for efficient metadata management and quick access to both detailed and summary information about the file group.

**Sample Manifest Summary File**

.. code-block:: python

    {
        "n_files": 50,
        "total_size": 600_000_000, # 600 MB
        "total_records": 100_000,
        "uri": "s3://bucket/prefix/manifest.parquet",
        "fingerprint": "2d0175ad9416dc5fd7138546471738ca"
    }

**Sample Manifest Data File**

.. code-block::


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


Create a Manifest File
------------------------------------------------------------------------------
This example shows how to create a manifest file and write it to AWS S3 using this library.

.. dropdown:: example.py

    .. literalinclude:: ../../../tests/test_manifest.py
       :language: python
       :start-at: start1
       :end-at: end1
       :linenos:


Read a Manifest File
------------------------------------------------------------------------------
This example shows how to read a manifest file from AWS S3 using this library.

.. dropdown:: example.py

    .. literalinclude:: ../../../tests/test_manifest.py
       :language: python
       :start-at: start2
       :end-at: end2
       :linenos:


Feature - Group Files Planner
------------------------------------------------------------------------------
The Group Files Planner is a sophisticated tool designed for efficient management of large-scale data processing tasks. It intelligently organizes vast numbers of files into manageable groups based on size or data volume. This feature excels in two key areas:

1. Enhancing parallel processing by distributing file groups among multiple workers.
2. Optimizing data lakes through strategic file compaction.

Using advanced algorithms, the Group Files Planner creates approximately equal-sized file groups, enabling efficient task allocation and improved data organization. Its high-performance implementation can rapidly process millions of files, making it an essential component for orchestrating data operations at scale, from terabytes to petabytes.

See :ref:`group-files-planner` section to see the benchmark of this algorithm.

This example shows how to use this library to group files.

.. dropdown:: example.py

    .. literalinclude:: ../../../tests/test_manifest.py
       :language: python
       :start-at: start3
       :end-at: end3
       :linenos:
