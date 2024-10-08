.. _release_history:

Release and Version History
==============================================================================


x.y.z (Backlog)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.4.1 (2024-08-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**Features and Improvements**

- Add ``ManifestFile.details`` attribute. It is a dictionary that contains additional information about the manifest file.


0.3.1 (2024-08-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**💥Breaking Changes**

- ``group_files``, ``ManifestFile.group_files_into_tasks_by_size``, ``ManifestFile.group_files_into_tasks_by_n_record`` now returns ``List[Tuple[List[T_DATA_FILE, int]]]`` instead of ``List[List[T_DATA_FILE]]``.


0.2.1 (2024-08-10)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
**💥Breaking Changes**

- Remove ``md5`` key from Data File typed dictionary, add ``etag`` key instead.
- Remove ``ManifestFile.group_files_into_tasks`` from public API.


**Features and Improvements**

- Add the following public APIs:
    - ``ManifestFile.group_files_into_tasks_by_size``
    - ``ManifestFile.group_files_into_tasks_by_n_record``
- Add fingerprint attribute to ``ManifestFile`` class. It is a unique fingerprint for the manifest file. It is calculated based on the URI and ETag of the data files.


**Minor Improvements**

**Bugfixes**

**Miscellaneous**


0.1.1 (2024-08-08)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
- First release
