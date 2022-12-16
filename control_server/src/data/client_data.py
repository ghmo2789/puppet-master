from typing import Optional, Any

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data_class import DataClass


class ClientData(DataClass, Serializable, Deserializable):
    """
    A data class containing client data.
    """
    def __init__(self):
        super().__init__()
        self.os_name: Optional[str] = None
        self.os_version: Optional[str] = None
        self.hostname: Optional[str] = None
        self.host_user: Optional[str] = None
        self.privileges: Optional[str] = None
        self.host_id: Optional[str] = None
        self.polling_time: Optional[int] = None

    @staticmethod
    def load_from_dict(data_dict: dict, raise_error: bool = True):
        return DataClass._try_load_from_dict(
            instance=ClientData(),
            data_dict=data_dict,
            raise_error=raise_error
        )

    def serialize(self, _: dict[str, Any] = None):
        return self.__dict__
