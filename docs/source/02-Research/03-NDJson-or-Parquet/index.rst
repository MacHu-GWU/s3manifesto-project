.. _ndjson-or-parquet:

NDJson or Parquet
==============================================================================
Manifest 文件本质上是一对 Data File 的 metadata. 而一个 Data File 的 metadata 可以被抽象视为一个 schema 不变的 Struct 对象. 那么我们应该选择哪种格式用来存储这个 Struct 对象呢? 一般来说, 我们有两种选择: NDJson 和 Parquet. 下面这个脚本测试了两种格式的读写性能.

.. dropdown:: ndjson_or_parquet.py

    .. literalinclude:: ./ndjson_or_parquet.py
       :language: python
       :linenos:

结论:

Parquet 是最优选择. 它不仅有最好的 IO 性能, 并且由于其列式存储的特性, 还能选择性地读部分字段, 例如只读 URI 字段用来定位数据文件. 并且将它读到 DataFrame 中做后续处理也更方便.
