TypedDict
==============================================================================
在处理大量 (百万级以上) 数据文件的 metadata 时无论使用 dataclasses, attrs 还是 pydantic 都会有额外的性能开销. 因为我的数据是可信的, 我不需要序列化和反序列化以及 validation 这些功能. 所以我希望用 TypedDict 来替代这些库. 该脚本测试了这一做法的可行性.

.. dropdown:: typeddict_poc.py

    .. literalinclude:: ./typeddict_poc.py
       :language: python
       :linenos:
