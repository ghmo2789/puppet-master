from typing import Any, cast

from control_server.src.data.anonymous_client_task_response import \
    AnonymousClientTaskResponse
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data_class import DataClass


class ClientTaskResponseCollection(DataClass, Deserializable, Serializable):
    """
    A collection data class of a specific clients responses to a specific task
    """
    def __init__(
            self,
            client_id: str = None,
            task_id: str = None,
            responses: list[AnonymousClientTaskResponse] = None):
        super().__init__()
        self.responses: list[AnonymousClientTaskResponse] = \
            responses if responses is not None else []

        self._id = {
            "client_id": client_id,
            "task_id": task_id
        }

    def get_client_id(self):
        return self.id["client_id"]

    def get_task_id(self):
        return self.id["task_id"]

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
