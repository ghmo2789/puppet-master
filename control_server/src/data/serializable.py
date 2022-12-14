from abc import ABC
from typing import Any


class Serializable(ABC):
    """
    Interface class representing serializable objects, with default
    implementation for serialization method.
    """

    def serialize(self, data_dict: dict[str, Any] = None) -> dict[str, Any]:
        serialized_dict = data_dict if data_dict is not None else \
            self.__dict__.copy()

        for (key, value) in serialized_dict.items():
            if isinstance(value, Serializable):
                serialized_dict[key] = value.serialize()
            elif hasattr(value, "__dict__") or isinstance(value, dict):
                existing_dict = value.__dict__.copy() \
                    if hasattr(value, "__dict__") else value

                inner_dict = {}
                serialized_dict[key] = inner_dict

                for (inner_key, inner_value) in existing_dict.items():
                    if isinstance(inner_value, Serializable):
                        inner_dict[inner_key] = inner_value.serialize()
                    else:
                        inner_dict[inner_key] = inner_value

                serialized_dict[key] = inner_dict
            elif hasattr(value, '__iter__') and not isinstance(value, str):
                inner_list = []

                for entry in value:
                    if isinstance(entry, Serializable):
                        inner_list.append(entry.serialize())
                    else:
                        inner_list.append(entry)

                serialized_dict[key] = inner_list

        return serialized_dict
