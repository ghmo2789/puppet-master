from typing import Any, Callable
from abc import ABC


class DataClass(ABC):
    def __init__(self):
        pass

    def __str__(self):
        outputs = []
        for property_name in self.get_properties():
            outputs.append(
                f"{property_name}: {str(getattr(self, property_name))}")

        return ", ".join(outputs)

    def get_properties(self):
        return [(key, type(value)) for (key, value) in vars(self).items()]

    def _load_data(self,
                   data_reader: Callable[[str, type], Any],
                   validate_types: bool = False,
                   raise_error: bool = True):
        for property_name, property_type in self.get_properties():
            prop_value = data_reader(property_name, property_type)

            if prop_value is None:
                if raise_error:
                    raise ValueError(f'Property "{property_name}" is None')

                return False

            if validate_types and not isinstance(prop_value, property_type):
                if raise_error:
                    raise TypeError(
                        f'Property mismatch: setting "{property_name}" ' +
                        f'is of type "{type(prop_value)}" but "{property_type}" '
                        f'was expected.')

                return False

        for property_name, property_type in self.get_properties():
            setattr(
                self,
                property_name,
                data_reader(property_name, property_type)
            )

        return True

    def load_from_with_types(
            self,
            data_reader: Callable[[str, type], Any],
            raise_error: bool = True):
        return self._load_data(
            data_reader,
            validate_types=True,
            raise_error=raise_error
        )

    def load_from(
            self,
            data_reader: Callable[[str], Any],
            raise_error: bool = True):
        return self._load_data(
            (lambda prop, prop_type: data_reader(prop)),
            validate_types=False,
            raise_error=raise_error
        )
