.. _ndjson-or-parquet:

NDJson or Parquet
==============================================================================
Manifest files are essentially metadata for pairs of Data Files. A Data File's metadata can be abstractly viewed as a Struct object with an invariant schema. So which format should we choose to store this Struct object? Generally, we have two options: NDJson and Parquet. The following script tests the read/write performance of both formats.

.. dropdown:: ndjson_or_parquet.py

    .. literalinclude:: ./ndjson_or_parquet.py
       :language: python
       :linenos:

Conclusion:

Parquet is the optimal choice. It not only has the best I/O performance, but due to its columnar storage characteristics, it also enables selective reading of partial fields, such as reading only the URI field to locate data files. Additionally, loading it into a DataFrame for subsequent processing is more convenient.
