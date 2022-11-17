from typing import List

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data.task import Task
from control_server.src.data_class import DataClass


class ClientTaskCollection(DataClass, Serializable, Deserializable):
    def __init__(self):
        super().__init__()
        self.tasks: List[Task] = []

    @staticmethod
    def load_from_dict(data_dict: dict, raise_error: bool = True):
        return DataClass._try_load_from_dict(
            instance=ClientTaskCollection(),
            data_dict=data_dict,
            raise_error=raise_error
        )
