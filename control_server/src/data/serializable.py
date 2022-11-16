from abc import ABC


class Serializable(ABC):
    """
    Interface class representing serializable objects, with default
    implementation for serialization method.
    """
    def serialize(self):
        serialized_dict = self.__dict__

        for (key, value) in serialized_dict.items():
            if isinstance(value, Serializable):
                serialized_dict[key] = value.serialize()
            elif hasattr(value, "__dict__"):
                serialized_dict[key] = value.__dict__

        return serialized_dict
