from datetime import datetime
from typing import Dict

from control_server.src.data.client_data import ClientData
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable


class IdentifyingClientData(Serializable, Deserializable):
    """
    A class containing all data required to identify a client. This includes
    the client's IP address and the client's data.
    """

    def __init__(
            self,
            client_data: ClientData = None,
            ip: str = None,
            data_dict: Dict = None,
            last_seen: str = None,
            first_seen: str = None):
        self.client_data = client_data
        self.ip = ip
        self.first_seen: str = first_seen
        self.last_seen: str = last_seen
        self._id = None

        if data_dict is not None:
            self.__dict__ = data_dict

    def get_first_seen(self) -> datetime:
        return datetime.fromisoformat(self.first_seen)

    def set_last_seen(self, time: datetime):
        self.last_seen = time.isoformat()

    def get_last_seen(self) -> datetime:
        return datetime.fromisoformat(self.last_seen)

    @property
    def id(self):
        return self._id

    def set_id(self, new_id: str):
        self._id = new_id
        return self
