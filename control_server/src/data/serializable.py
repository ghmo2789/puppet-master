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
            elif hasattr(value, "__dict__") or isinstance(value, dict):
                existing_dict = value.__dict__ \
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
