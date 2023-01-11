from datetime import datetime, timedelta
from typing import Dict, Any, cast

from control_server.src.data.client_data import ClientData
from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.utils.time_utils import time_now


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
            first_seen: str = None
    ):
        self.client_data = client_data
        self.ip = ip
        self.first_seen: str = first_seen
        self.last_seen: str = last_seen
        self._id = None

        if data_dict is not None:
            self.__dict__ = data_dict

    def time_since_last_seen(self) -> timedelta:
        last_seen_time = datetime.fromisoformat(self.last_seen)
        return time_now() - last_seen_time

    def is_online(self) -> bool:
        if self.last_seen is None:
            return False

        total_seconds = self.time_since_last_seen().total_seconds()
        return total_seconds <= self.client_data.polling_time * 2

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

    def deserialize(self, data_dict: dict[str, Any]) -> Deserializable:
        super().deserialize(data_dict=data_dict)

        if self.client_data is not None and 'client_data' in data_dict:
            self.client_data = ClientData().deserialize(
                data_dict['client_data']
            )

        return self
