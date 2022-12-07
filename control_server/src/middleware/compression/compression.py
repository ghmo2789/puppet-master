from __future__ import annotations

from typing import Tuple, Callable

from decouple import config

from control_server.src.middleware.compression.compression_method \
    import CompressionMethod


class Compression:
    """
    Class representing a data compression method, with support for compression
    and decompression.
    """
    methods: dict[
        CompressionMethod,
        Tuple[Callable[[bytes], bytes], Callable[[bytes], bytes]]
    ] = {
        CompressionMethod.BROTLI: CompressionMethod.get_brotli()
    }

    override_compression: Compression = None

    def __init__(
            self,
            use_compression: bool = True,
            compression_method: CompressionMethod = CompressionMethod.BROTLI
    ):
        self._compression = use_compression

        self._compressor, self._decompressor = \
            Compression.methods[compression_method] \
                if use_compression else \
                (None, None)

    @staticmethod
    def read_from_settings() -> Compression:
        """
        Reads the compression setting from the settings file.
        :return: None
        """
        if Compression.override_compression is not None:
            return Compression.override_compression

        use_compression = config(
            'UDP_COMPRESSION',
            cast=bool,
            default=True
        )

        method_name = config(
            'UDP_COMPRESSION_METHOD',
            cast=str,
            default=CompressionMethod.BROTLI.name
        )

        return Compression(
            use_compression=use_compression,
            compression_method=CompressionMethod[method_name]
        )

    def compress(self, data: bytes):
        """
        Applies the defined compression method to the specified bytes, or returns
        the data unchanged if compression is disabled.
        :return: A bytes object representing the compressed data.
        """
        if not self._compression:
            return data

        return self._compressor(data)

    def decompress(self, data: bytes):
        """
        Decompresses the specified bytes with the defined compression method, or
        returns the data unchanged if compression is disabled.
        :return: A bytes object representing the decompressed data.
        """
        if not self._compression:
            return data

        return self._decompressor(data)
