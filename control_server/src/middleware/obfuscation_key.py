import os
from itertools import cycle

from decouple import config


class ObfuscationKey:
    static_key: bytes | None = None

    def __init__(self, key: bytes | None):
        self._key = key

    @staticmethod
    def get_key():
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
        ObfuscationKey.static_key = key

    @staticmethod
    def _read_file(file_path: str) -> str:
        with open(file_path, 'rb') as file:
            return file.read().decode('utf-8')

    def apply(self, data: bytes) -> bytes:
        if self._key is None:
            return data

        return bytes(
            x ^ y for (x, y) in zip(data, cycle(self._key))
        )


class StaticObfuscationKey:
    def __enter__(self):
        ObfuscationKey.set_static_key(
            key=os.urandom(1024)
        )

    def __exit__(self, exc_type, exc_val, exc_tb):
        ObfuscationKey.set_static_key(
            key=None
        )
