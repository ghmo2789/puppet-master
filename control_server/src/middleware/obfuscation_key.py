import os
from itertools import cycle

from decouple import config


class ObfuscationKey:
    static_key: bytes | None = None

    def __init__(self, key: bytes | None):
        self._key = key

    @staticmethod
    def get_key():
        """
        Gets the obfuscation key. If a static key is set, it will be used.
        Otherwise, the key will be read from the file specified as
        OBFUSCATION_KEY_FILE in the settings file. If the file does not exist,
        no obfuscation will be used.
        :return:
        """
        if ObfuscationKey.static_key is not None:
            return ObfuscationKey(
                key=ObfuscationKey.static_key
            )

        key_file = config(
            'OBFUSCATION_KEY_FILE',
            cast=str,
            default=''
        )

        if key_file is None or len(key_file) < 1:
            return ObfuscationKey(
                key=None
            )

        return ObfuscationKey(
            key=bytes.fromhex(
                ObfuscationKey._read_file(
                    file_path=key_file
                )
            )
        )

    @staticmethod
    def set_static_key(key: bytes | None):
        """
        Sets the static obfuscation key to the specified key. Setting this key
        will cause all future calls to get_key() to return an ObfuscationKey
        with the specified key, overriding the key file specified in the
        settings file.
        :param key: The key to set. If None, the static key will be cleared.
        :return: None
        """
        ObfuscationKey.static_key = key

    @staticmethod
    def _read_file(file_path: str) -> str:
        with open(file_path, 'rb') as file:
            return file.read().decode('utf-8')

    def apply(self, data: bytes) -> bytes:
        """
        Applies the obfuscation key to the specified data. If the key is None,
        the data will be returned unchanged.
        :param data: The data to obfuscate
        :return: The obfuscated data, or the original data if the key is None.
        """
        if self._key is None:
            return data

        return bytes(
            x ^ y for (x, y) in zip(data, cycle(self._key))
        )


class StaticObfuscationKey:
    """
    Helper class allowing a randomly generated static obfuscation key to be used
    temporarily with Python's with statement.
    """
    def __enter__(self):
        ObfuscationKey.set_static_key(
            key=os.urandom(1024)
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        ObfuscationKey.set_static_key(
            key=None
        )
