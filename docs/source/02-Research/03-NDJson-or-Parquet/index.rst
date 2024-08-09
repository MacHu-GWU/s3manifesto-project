NDJson or Parquet
==============================================================================
Manifest 文件本质上是一对 Data File 的 metadata. 而一个 Data File 的 metadata 可以被抽象视为一个 schema 不变的 Struct 对象. 那么我们应该选择哪种格式用来存储这个 Struct 对象呢? 一般来说, 我们有两种选择: NDJson 和 Parquet.

.. dropdown:: ndjson_or_parquet.py

    .. literalinclude:: ./ndjson_or_parquet.py
       :language: python
       :linenos:

结论:

用 Parquet.
