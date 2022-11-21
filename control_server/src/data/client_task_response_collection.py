from typing import Any, cast

from control_server.src.data.anonymous_client_task_response import \
    AnonymousClientTaskResponse
from control_server.src.data.client_task_response import ClientTaskResponse
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data_class import DataClass


class ClientTaskResponseCollection(DataClass, Deserializable, Serializable):
    def __init__(
            self,
            client_id: str = None,
            task_id: str = None,
            responses: list[AnonymousClientTaskResponse] = None):
        super().__init__()
        self.client_id: str = client_id
        self.task_id: str = task_id
        self.responses: list[AnonymousClientTaskResponse] = \
            responses if responses is not None else []

        self._id = {
            "client_id": self.client_id,
            "task_id": self.task_id
        }

    @property
    def id(self):
        return self._id

    def deserialize(self, data_dict: dict[str, Any]) -> Deserializable:
        super().deserialize(data_dict=data_dict)
        self.responses = [
            AnonymousClientTaskResponse().deserialize(cast(dict, response))
            for response in self.responses
        ]

        return self
