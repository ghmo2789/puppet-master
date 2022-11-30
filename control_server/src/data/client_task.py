from typing import Dict, cast

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data.task import Task
from control_server.src.data.task_status import TaskStatus
from control_server.src.data_class import DataClass


class ClientTask(DataClass, Serializable, Deserializable):
    """
    Data class representing a task assigned to a client
    """

    def __init__(
            self,
            client_id: str = None,
            task_id: str = None,
            task: Task = None):
        super().__init__()
        self._id: Dict[str, str] = {}

        if task_id is not None and client_id is not None:
            self.set_id(task_id, client_id)

        self.task = task
        self.status: str | None = None
        self.status_code: int | None = None

    def set_status_code(self, status_code: int):
        self.status_code = status_code

        if status_code >= TaskStatus.ERROR.get_code():
            self.status = TaskStatus.ERROR.get_name()
        elif status_code <= TaskStatus.IN_PROGRESS.get_code():
            self.status = TaskStatus.IN_PROGRESS.get_name()
        else:
            self.status = TaskStatus.DONE.get_name()

    def set_status(self, status: TaskStatus):
        self.status = status.get_name()
        self.status_code = status.get_code()

    @property
    def id(self) -> Dict[str, str]:
        return self._id

    def get_task_id(self) -> str:
        return self._id["task_id"]

    def get_client_id(self) -> str:
        return self._id["client_id"]

    def set_id(self, task_id: str, client_id: str):
        if task_id is None or client_id is None:
            raise ValueError("Task ID and client ID must be set")

        self._id = {
            "client_id": client_id,
            "task_id": task_id
        }

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
