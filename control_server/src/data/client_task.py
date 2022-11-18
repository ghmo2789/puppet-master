from typing import List, Dict, cast

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data.task import Task
from control_server.src.data_class import DataClass


class ClientTask(DataClass, Serializable, Deserializable):
    def __init__(
            self,
            client_id: str = None,
            task_id: str = None,
            task: Task = None):
        super().__init__()
        self.client_id = client_id
        self.task_id = task_id if task_id is not None else \
            (task.task_id if task is not None else None)

        self._id = client_id + "_" + self.task_id \
            if client_id is not None and self.task_id is not None else None

        self.task = task

    @property
    def id(self):
        return self._id

    @staticmethod
    def load_from_dict(data_dict: dict, raise_error: bool = True):
        return DataClass._try_load_from_dict(
            instance=ClientTask(),
            data_dict=data_dict,
            raise_error=raise_error
        )

    def deserialize(self, data_dict: Dict):
        super().deserialize(data_dict)

        self.task = Task().deserialize(cast(Dict, self.task))
        return self
