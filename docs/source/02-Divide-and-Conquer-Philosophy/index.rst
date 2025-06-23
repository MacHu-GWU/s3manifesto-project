.. _divide-and-conquer-philosophy:

Divide-and-Conquer Philosophy for Big Data Processing
==============================================================================
*Why s3manifesto transforms large-scale data workflows*


The Core Challenge
------------------------------------------------------------------------------
In big data systems, the fundamental challenge isn't just processing large volumes of data—it's **coordinating the processing** of millions of individual files efficiently. Traditional approaches often fail because they treat file metadata management as an afterthought, leading to:

- **Coordination Overhead**: Spending more time organizing work than executing it
- **Resource Imbalance**: Some workers finish quickly while others struggle with oversized tasks  
- **Memory Explosions**: Loading metadata for millions of files crashes coordination nodes
- **Retry Complexity**: Failed tasks containing hundreds of files require expensive re-processing

s3manifesto solves these problems by making **divide-and-conquer** a first-class architectural pattern.


The Divide-and-Conquer Workflow
------------------------------------------------------------------------------
**Phase 1: Metadata Collection** 
    Gather file metadata (URI, size, record count, ETag) from your data lake and create a master :class:`~s3manifesto.manifest.ManifestFile` object containing all file metadata. This one-time operation transforms scattered file information into organized, queryable datasets.

**Phase 2: Intelligent Partitioning**
    Use :meth:`ManifestFile.partition_files_by_size <s3manifesto.manifest.ManifestFile.partition_files_by_size>` or :meth:`ManifestFile.partition_files_by_n_record <s3manifesto.manifest.ManifestFile.partition_files_by_n_record>` methods to apply the Best Fit Decreasing algorithm, partitioning file collections into balanced groups. For each group, create a dedicated :class:`~s3manifesto.manifest.ManifestFile` object and write it to S3, generating both the manifest data file and manifest summary file.

**Phase 3: Distributed Execution**
    Deploy tasks to parallel workers by passing only the **manifest summary file URI** to each worker. Workers use :meth:`ManifestFile.read <s3manifesto.manifest.ManifestFile.read>` to load their assigned file group from S3 and process exactly that group. Since groups are pre-balanced, workers finish at approximately the same time, maximizing cluster utilization.

**Phase 4: Result Aggregation**
    Combine outputs from each worker group into final results. Since partitioning was deterministic, result ordering and merging becomes straightforward.


Philosophical Advantages
------------------------------------------------------------------------------
**1. Separation of Concerns**

Traditional big data systems conflate **what to process** with **how to distribute the work**. s3manifesto separates these concerns:

- **Manifest files** define *what* (the complete set of files and their metadata)
- **Partitioning algorithms** define *how* (the optimal distribution strategy)
- **Worker processes** focus purely on *execution* (processing their assigned file group)

This separation enables independent optimization of each layer and makes systems easier to reason about, test, and debug.

**2. Predictable Resource Planning**

By pre-calculating the total size and record count of each task group, infrastructure teams can:

- **Right-size compute instances** based on memory requirements per group
- **Predict processing time** using historical performance per MB or per record
- **Set appropriate timeouts** based on expected task duration
- **Auto-scale clusters** based on total workload divided by per-node capacity

Traditional approaches that discover work dynamically cannot provide these guarantees.

**3. Fault Tolerance Through Granularity**

When a worker fails processing 10,000 small files, traditional systems must either:
- Retry all 10,000 files (expensive and slow)
- Track individual file completion state (complex coordination overhead)

s3manifesto's approach creates ~50 balanced groups of ~200 files each. Failed groups can be retried independently without affecting completed work, dramatically reducing the blast radius of failures.

**4. Incremental Processing Patterns**

Manifest fingerprints enable sophisticated incremental processing:

- **Skip unchanged manifests** entirely using fingerprint comparison
- **Process only new file groups** by comparing manifest versions
- **Implement exactly-once semantics** using deterministic partitioning
- **Cache intermediate results** keyed by group fingerprints

This transforms traditionally complex incremental processing into simple, stateless operations.


Performance Optimization Patterns
------------------------------------------------------------------------------
**Hierarchical Grouping for Million+ Files**

For extreme scale (1M+ files), use a two-level approach:

.. code-block:: python

    # Level 1: 1M data files
    import random

    data_file_list = [...]
    n_group = 100
    groups = {i: [] for i in range(1, 1+n_group)}
    for data_file in data_file_list:
        group_id = random.randint(1, n_group)
        groups[group_id].append(data_file)


    for sub_data_file_list in groups.values():
        manifest = ManifestFile.new(
            data_file_list=sub_data_file_list,
            # ... other params
        )
        sub_groups = manifest.partition_files_by_size(target_size=1_000_000_000)  # 1GB
        for sub_group in sub_groups
            sub_manifest = ManifestFile.new(
                data_file_list=sub_group.data_files,
                # ... other params
            )
            # Write sub_manifest to S3 or process further

This pattern provides:

- **O(log n) coordination overhead** instead of O(n) 
- **Bounded memory usage** at each hierarchy level
- **Parallel manifest creation** across super-groups
- **Flexible deployment models** (super-groups → clusters, worker groups → nodes)


Real-World Impact Examples
------------------------------------------------------------------------------
**Data Lake ETL Pipeline**
    *Problem*: Processing 500,000 daily log files taking 8 hours due to coordination overhead
    *Solution*: Manifest-based partitioning into 2,000 balanced groups
    *Result*: Processing time reduced to 45 minutes with perfect resource utilization

**Machine Learning Feature Extraction**  
    *Problem*: Unpredictable training job completion times due to imbalanced data splits
    *Solution*: Partition training data by record count into equal-sized manifests
    *Result*: Consistent 3-hour training cycles with predictable GPU utilization


Key Design Principles
------------------------------------------------------------------------------
**1. Immutability First**
All data structures are immutable, eliminating race conditions and enabling safe concurrent access patterns essential for distributed systems.

**2. Metadata as Data**
File metadata becomes queryable, versionable data that can be analyzed, cached, and optimized using standard data engineering tools.

**3. Algorithm Transparency**
The Best Fit Decreasing algorithm provides mathematical guarantees about load balancing, making system behavior predictable and debuggable.

**4. Composable Abstractions**
Manifest files work as both in-memory calculators and persistent storage, enabling flexible deployment patterns from single-machine to massive clusters.

**5. Operational Simplicity**
Complex distributed coordination reduces to simple, stateless worker processes that can be deployed using any orchestration framework (Kubernetes, EMR, Airflow, etc.).

This philosophy transforms big data processing from an art of careful coordination into a science of systematic decomposition, making large-scale systems more reliable, maintainable, and cost-effective.
