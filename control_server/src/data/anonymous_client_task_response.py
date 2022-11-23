from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data_class import DataClass


class AnonymousClientTaskResponse(DataClass, Deserializable, Serializable):
    """
    Client response data class, without specifying the task which the response
    is to.
    """
    def __init__(
            self,
            result: str = None,
            status: int = None):
        super().__init__()
        self.result: str = result
        self.status: int = status
