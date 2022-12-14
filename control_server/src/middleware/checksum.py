from __future__ import annotations

from decouple import config


class Checksum:
    """
        Class representing a data compression method, with support for compression
        and decompression.
        """
    override_checksum: Checksum = None

    def __init__(
            self,
            method: str = 'fastcrc.crc16.gsm'
    ):
        self._checksum_method = Checksum.get_checksum_method(method)

    @staticmethod
    def get_checksum_method(method: str):
        import fastcrc as fastcrc
        libraries = {
            'fastcrc': fastcrc,
        }

        split_method = method.split('.')
        method_lib = split_method[0]

        if method_lib not in libraries:
            raise ValueError(
                f'Invalid checksum method library: {method_lib}')

        actual_method = libraries[method_lib]
        for entry in split_method[1:]:
            actual_method = getattr(actual_method, entry)

        return actual_method

    @staticmethod
    def get_default() -> Checksum:
        return Checksum.override_checksum

    @staticmethod
    def read_from_settings() -> Checksum:
        """
        Reads the compression setting from the settings file.
        :return: None
        """
        if Checksum.override_checksum is not None:
            return Checksum.override_checksum

        method = config(
            'CHECKSUM_METHOD',
            cast=str,
            default='fastcrc.crc16.gsm'
        )

        return Checksum(
            method=method
        )

    def calculate_checksum(self, data: bytes) -> int:
        """
        Calculates the checksum for the given data.
        :param data: The data to calculate the checksum for
        :return: The checksum, as an int
        """
        return self._checksum_method(data)

    def is_match(self, data: bytes, checksum: int) -> bool:
        """
        Checks if the given data matches the given checksum.
        :param data: The data to check
        :param checksum: The checksum to check
        :return: True if the checksum matches, False otherwise
        """
        return self.calculate_checksum(data) == checksum
