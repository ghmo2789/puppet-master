import hashlib
import json
import re
from typing import Any, Iterable, Dict, List
from uuid import UUID

from decouple import Csv, config

from control_server.src.data.serializable import Serializable


class ClientIdGenerator:
    """
    Class generating IDs based on data contained within a serializable object.
    """

    def __init__(self, id_key: str, client_id_keys: List[str] = None):
        self._id_key = id_key
        self._hash_func = hashlib.sha256
        self.encoding = 'utf-8'
        self.keys = client_id_keys or config(
            'CLIENT_ID_KEYS',
            cast=Csv(
                strip=' '
            ),
            default='^.*$'
        )

        self.key_regex = [re.compile(key) for key in self.keys]
        self.key_cache: dict[str, bool] = {}

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

    def update_key_cache(self, key: str):
        """
        Updates the key cache with the given key.
        :param key: The key to update the cache with.
        :return:
        """
        if key in self.key_cache:
            return self.key_cache[key]

        result = self.key_cache[key] = any(
            [
                regex.match(key) for regex in self.key_regex
            ]
        )

        return result

    def build_serialized_dict(
            self,
            data: Dict[str, Any],
            current_key: str | None = None
    ):
        """
        Recursively builds a dict from the given dict, which is a subset of the
        given dict, that contains only keys that match any of the regexes
        specified in the constructor.
        :param current_key: The starting key, used in recursive calls to
        determine if child keys should be included in the returned dict.
        :param data: The dict to build a subset of.
        :return: A dict containing only keys that match any of the regexes
        specified in the constructor.
        """
        resulting_dict = {}
        for key, value in data.items():
            complete_key = key \
                if current_key is None else \
                f'{current_key}.{key}'

            if self.update_key_cache(complete_key):
                resulting_dict[key] = value
            elif isinstance(value, dict):
                sub_dict = self.build_serialized_dict(
                    current_key=complete_key,
                    data=value
                )

                if not any(sub_dict):
                    continue

                resulting_dict[key] = sub_dict

        return resulting_dict

    def generate(self, data: Serializable) -> UUID:
        """
        Generates a UUID based on the data contained within the given
        serializable object.
        :param data: The serializable object to generate a UUID from.
        :return: A UUID generated from the data contained within the given
        serializable object.
        """
        data = data.serialize()
        return self.generate_from_data(data)

    def generate_from_data(self, data: dict) -> UUID:
        """
        Generates a UUID based on the data contained within the given dict.
        :param data: The dict to generate a UUID from.
        :return: A UUID generated from the data contained within the given dict.
        """
        json_dict = self.build_serialized_dict(data=data)

        client_data_json = json.dumps(json_dict)
        client_data_hash = self.hash(client_data_json, self._id_key)

        # Take 16 bytes from the hash because UUIDs are 128 bits (16 bytes) long
        return UUID(bytes=client_data_hash[0:16])
