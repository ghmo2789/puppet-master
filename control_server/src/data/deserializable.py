from abc import ABC
from typing import Dict
from typing import get_type_hints

from munch import Munch


class Deserializable(ABC):
    """
    Interface class representing serializable objects, with default
    implementation for serialization method.
    """
    def deserialize(self, data_dict: Dict):
        types = get_type_hints(self.__class__)
        for (key, value) in data_dict.items():
            if value is Dict and key in types and types[key] is not Dict:
                setattr(self, key, Munch.fromDict(value))
            else:
                setattr(self, key, value)
        self.__dict__ = data_dict
        return self
