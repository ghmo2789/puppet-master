import hashlib
import json
from uuid import UUID

from control_server.src.data.serializable import Serializable


class ClientIdGenerator:
    """
    Class generating IDs based on data contained within a serializable object.
    """
    def __init__(self, id_key: str):
        self._id_key = id_key
        self._hash_func = hashlib.sha256
        self.encoding = 'utf-8'

    def hash(self, *args: str) -> bytes:
        """
        Hashes the given string arguments using the hash function specified in
        the constructor.
        :param args: The string arguments to hash.
        :return: The hash of the given arguments, as a bytes object.
        """
        hasher = self._hash_func()

        if len(args) < 1:
            raise ValueError("No arguments provided")

        for arg in args:
            if arg is None:
                raise ValueError("Invalid argument provided")

            hasher.update(arg.encode(encoding=self.encoding))

        return hasher.digest()

    def generate(self, data: Serializable) -> UUID:
        """
        Generates a UUID based on the data contained within the given
        serializable object.
        :param data: The serializable object to generate a UUID from.
        :return: A UUID generated from the data contained within the given
        serializable object.
        """
        client_data_json = json.dumps(data.serialize())
        client_data_hash = self.hash(client_data_json, self._id_key)

        # Take 16 bytes from the hash because UUIDs are 128 bits (16 bytes) long
        return UUID(bytes=client_data_hash[0:16])
