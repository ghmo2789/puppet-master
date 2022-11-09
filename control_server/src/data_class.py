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
        return vars(self).keys()

    def load_from(self, data_reader: Callable[[str], Any]):
        for property_name in self.get_properties():
            if data_reader(property_name) is None:
                return False

        for property_name in self.get_properties():
            setattr(self, property_name, data_reader(property_name))

        return True
