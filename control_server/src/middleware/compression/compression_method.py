from __future__ import annotations

from enum import Enum
from typing import Tuple, Callable


class CompressionMethod(Enum):
    """
    Enum used to represent the different compression methods
    """
    BROTLI = 1

    @staticmethod
    def get_brotli() -> \
            Tuple[Callable[[bytes], bytes], Callable[[bytes], bytes]]:
        """
        Gets the brotli compressors
        :return: A tuple of the compressors.
        """
        import brotli
        return \
            lambda data: brotli.compress(data, quality=11), \
            lambda data: brotli.decompress(data)
