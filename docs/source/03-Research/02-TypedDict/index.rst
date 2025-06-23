.. _typeddict:

TypedDict
==============================================================================
When processing large volumes (millions+) of data file metadata, using dataclasses, attrs, or pydantic introduces additional performance overhead. Since my data is trusted and I don't need serialization, deserialization, or validation features, I want to use TypedDict to replace these libraries. This script tests the feasibility of this approach.

.. dropdown:: typeddict_poc.py

    .. literalinclude:: ./typeddict_poc.py
       :language: python
       :linenos: