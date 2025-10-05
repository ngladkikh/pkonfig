"""Helper module that holds a logic to create helper _Descriptor class that is version agnostic."""

try:
    # Python 3.13+
    from typing import Descriptor as _Descriptor  # type: ignore
except ImportError:
    try:
        from typing_extensions import Descriptor as _Descriptor  # type: ignore
    except ImportError:
        # minimal runtime stub for runtime only
        class _Descriptor:  # type: ignore
            def __class_getitem__(cls, _):
                return cls
