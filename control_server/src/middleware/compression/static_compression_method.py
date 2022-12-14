from __future__ import annotations

from control_server.src.middleware.compression.compression_method \
    import CompressionMethod
from control_server.src.middleware.compression.compression \
    import Compression


class StaticCompressionMethod:
    """
    Utility class to support overriding the compression specified in settings
    with a specific one using python's with statement.
    """

    def __init__(self, method: CompressionMethod | None):
        self._method = method
        self._compression = Compression(
            use_compression=method is not None,
            compression_method=method
        )
        self._previous_override: Compression | None = None

    def __enter__(self):
        self.set()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.unset()

    def set(self):
        self._previous_override = Compression.override_compression
        Compression.override_compression = self._compression

    def unset(self):
        Compression.override_compression = self._previous_override
        self._previous_override = None
