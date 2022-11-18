from typing import List, Dict, cast

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data.task import Task
from control_server.src.data_class import DataClass


class ClientTaskCollection(DataClass, Serializable, Deserializable):
    def __init__(self, client_id: str = None, tasks: List[Task] = None):
        super().__init__()
        self._id = client_id
        self.tasks: List[Task] = tasks if tasks is not None else []

    @property
    def client_id(self):
        return self._id

    @staticmethod
    def load_from_dict(data_dict: dict, raise_error: bool = True):
        return DataClass._try_load_from_dict(
            instance=ClientTaskCollection(),
            data_dict=data_dict,
            raise_error=raise_error
        )

    def deserialize(self, data_dict: Dict):
        super().deserialize(data_dict)

        self.tasks = [
            Task().deserialize(task)
            for task in
            cast(List[Dict], self.tasks)
        ]
        return self
