from typing import Dict

from control_server.src.data.client_data import ClientData
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable


class IdentifyingClientData(Serializable, Deserializable):
    """
    A class containing all data required to identify a client. This includes
    the client's IP address and the client's data.
    """

    def __init__(self,
                 client_data: ClientData = None,
                 ip: str = None,
                 data_dict: Dict = None):
        self.client_data = client_data
        self.ip = ip
        self._id = None

        if data_dict is not None:
            self.__dict__ = data_dict

    def set_id(self, new_id: str):
        self._id = new_id
