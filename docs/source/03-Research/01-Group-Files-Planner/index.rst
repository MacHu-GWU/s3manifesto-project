.. _group-files-planner:

Group Files Planner
==============================================================================
n big data processing, divide-and-conquer strategies are commonly employed. When processing millions of files, typical use cases include:

- Dividing files into smaller groups (e.g., 1,000 files per group) and distributing them across multiple parallel workers to improve processing speed
- Performing data compaction in data lakes by merging small files to reduce I/O operations, improve data organization, and enhance query performance

The core challenge in these divide-and-conquer scenarios is efficiently grouping files by size (or data volume, typically record count) into groups of approximately equal size. When dealing with large data volumes, selecting a high-performance grouping algorithm becomes critical.


Implementation and Performance Benchmark
------------------------------------------------------------------------------
The following script implements this algorithm using both pure Python and the Polars library, with comprehensive performance testing results.

.. dropdown:: group_files_planner_poc.py

    .. literalinclude:: ./group_files_planner_poc.py
       :language: python
       :linenos:

**Performance Results**:

Testing with 1M files shows that the pure Python implementation completes in approximately 0.5 seconds, while the Polars implementation requires about 1 second. Processing time scales linearly with file count at a 1:1 ratio. For 100M files, the pure Python implementation takes approximately 50 seconds compared to 100 seconds for the Polars implementation.

Based on these results, our project primarily uses the pure Python algorithm implementation.

.. note::

    The Polars implementation uses cumulative sum, but many different algorithms exist for this grouping problem, each with distinct complexity and space utilization characteristics. This benchmark serves as a reference point only. In production, we use the Best Fit Decreasing (BFD) algorithm. For the specific implementation, refer to :func:`~s3manifesto.grouper.group_files`. We won't elaborate further on alternative approaches here.

.. note::

    Since our algorithm testing used pure numerical calculations while practical applications use dataclasses, there is additional performance overhead in real-world usage. In our business scenarios, we typically process between 100 and 1,000 files, with a maximum of 10,000 files. Our testing shows that processing 10,000 files takes approximately 1 second. Processing time grows slightly super-linearly with data volume at O(n*log n). For datasets exceeding 10,000 files, we can use random sampling to partition large datasets into smaller chunks, then apply this algorithm within each chunk.

    Below are our benchmark test results:

    - process 1k item in 0.02 sec
    - process 5k item in 0.30 sec
    - process 10k item in 1 sec
    - process 50k item in 12 sec
    - process 100k item in 37 sec
    - process 500k item in 7.5 min
    - process 1000k item in 24 min


Dispatcher Use Case
------------------------------------------------------------------------------
In big data processing workflows, an Orchestrator typically scans all file metadata and divides it into smaller groups for distribution to Workers. Based on our benchmark results (1 second to process 10,000 files), let's evaluate this algorithm's performance in big data divide-and-conquer scenarios using the Amazon Orders open-source dataset as a baseline (approximately 100,000 records compressed to 20MB, uncompressed to about 150MB).

- Assume we have 1PB of uncompressed data: 1PB / 150MB = 6.67M files
- Each distributed worker processes 1GB of data (approximately 6-7 files)
- We divide 6.67M files into 6,670 groups of ~1,000 files each
- Each group requires approximately 0.02 seconds to process
- Total processing time: 6,670 × 0.02 = 133 seconds (approximately 2.2 minutes)

The ability to process 1PB of data metadata in approximately 2 minutes demonstrates excellent performance characteristics, confirming the algorithm's suitability for large-scale big data scenarios.
