from control_server.src.data.serializable import Serializable
from control_server.src.data_class import DataClass


class ClientData(DataClass, Serializable):
    """
    A data class containing client data.
    """
    def __init__(self):
        super().__init__()
        self.os_name = None
        self.os_version = None
        self.hostname = None
        self.host_user = None
        self.privileges = None

    @staticmethod
    def load_from_dict(data_dict: dict, raise_error: bool = True):
        return DataClass._try_load_from_dict(
            instance=ClientData(),
            data_dict=data_dict,
            raise_error=raise_error
        )

    def serialize(self):
        return self.__dict__
