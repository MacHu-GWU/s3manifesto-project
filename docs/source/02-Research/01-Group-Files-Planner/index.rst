.. _group-files-planner:

Group Files Planner
==============================================================================
在大数据处理中, 经常会用到分儿治之的策略. 举例来说, 在百万级文件数量的数据处理中, 会有如下应用场景:

- 将文件分成小组, 例如每组 1000 个文件, 交给许多分布式的 worker 并行处理, 提高处理速度.
- 对 datalake 中的数据文件做 compaction, 将小文件合并使得文件的 IO 次数减少, 数据更有序, 查询性能更高.

这种分而治之的应用场景的核心技术是将文件按照大小 (或是里面的数据量, 通常是行数) 聚合成固定大小 (不是严格等于, 大致就可以) 的 Group. 在数据量很大的时候, 选择一个高性能的分组算法就变得很重要了.


Implementation and Performance Benchmark
------------------------------------------------------------------------------
下面这个脚本我们分别用纯 Python 和用 polars 库实现了这个算法, 并测试了性能.

.. dropdown:: group_files_planner_poc.py

    .. literalinclude:: ./group_files_planner_poc.py
       :language: python
       :linenos:

**结论**:

对于 1M 个文件进行测试, 纯 Python 实现大约是 0.5 秒, 而 Polars 实现大约是 1 秒. 随着文件的数量增加耗时也 1:1 线性增加. 在 100M 个文件时纯 Python 实现大约是 50 秒. 而 Polars 实现大约是 100 秒.

所以我的项目中主要采用纯 Python 实现的算法.

.. note::

    另外, polars 中的实现用的是 cumulated sum, 而这种分包算法其实有很多种不同的算法, 它们的复杂度, 以及空间利用率等都不一样. 这里的测试只是一个简单的 benchmark, 仅供参考. 实际我们使用的是 Best Fit Decreasing (BFD) 算法, 请参考 :func:`~s3manifesto.grouper.group_files` 的具体实现. 这里就不赘述了.

.. note::

    由于我们测试算法时用的是纯数字计算, 而实际应用中则要用 dataclass, 所以会有很多性能损耗. 在我们的业务场景下, 一般会处理的文件数量在 100 ~ 1000 之间, 最多不会超过 10K. 而在我们的测试下, 处理 10K 个文件的分包的耗时大约是 1 秒. 耗时基本上是随着数据量的增大线性多一点增长 O(n*logN). 如果数据量实在太多, 例如在 10K 以上, 我们就可以简单的通过随机采样将大数据分拆成小包, 然后在小包内再使用这个算法.

    下面是我们的测试的 benchmark 结果:

    - process 1k item in 0.02 sec
    - process 5k item in 0.30 sec
    - process 10k item in 1 sec
    - process 50k item in 12 sec
    - process 100k item in 37 sec
    - process 500k item in 7.5 min
    - process 1000k item in 24 min


Dispatcher Use Case
------------------------------------------------------------------------------
在大数据处理时, 我们往往会 Orchestrator 扫描全部文件的 metadata, 然后将其分成小组分发给 Worker 来处理. 那么根据以上的 benchmark (1 秒处理 10K 个文件), 以 Amazon Order 开源数据集为基准 (大约 100K 条数据压缩后是 20MB, 未压缩大约是 150MB), 测试一下这个算法在大数据分而治之的场景下的性能.

- 我们来假设有 1PB (未压缩) 的数据量. 相当于 1PB / 150MB = 6666K 个文件 (未压缩).
- 我们的每一个分布式 worker 应该处理 1GB 的数据量 (大该 6-7 个文件).
- 那么我们会将 6666K 个文件分成 6666K / 1000 = 6666 个小组.
- 每个小组大约需要 0.02 sec 来处理, 所以总计处理时间大约是 6666 * 0.02 = 133.32 秒, 也就是大约 2 分钟.

在 2 分钟内处理 1PB 数据的 metadata, 这个性能是非常不错的, 证明它完全适用于大数据场景.
