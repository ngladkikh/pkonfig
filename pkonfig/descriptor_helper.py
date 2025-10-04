"""Helper module that holds a logic to create helper _Descriptor class that is version agnostic."""

try:
    # Python 3.13+
    from typing import Descriptor as _Descriptor
except ImportError:
    try:
        from typing_extensions import Descriptor as _Descriptor  # type: ignore
    except ImportError:
        class _Descriptor:  # minimal runtime stub for runtime only
            def __class_getitem__(cls, item):
                return cls