import uuid

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.serializable import Serializable
from control_server.src.data_class import DataClass


class Task(DataClass, Serializable, Deserializable):
    """
    A class representing a client task
    """

    def __init__(
            self,
            name: str = None,
            data: str = None,
            min_delay: int = None,
            max_delay: int = None,
            time: str = None):
        super().__init__()
        self.name: str = name
        self.data: str = data
        self.min_delay: int = min_delay
        self.max_delay: int = max_delay
        self.id: str | None = None
        self.created_time: str = time

    def generate_id(self):
        self.id = str(uuid.uuid4())

    def with_id(self):
        self.generate_id()
        return self

    def serialize(self):
        return self.__dict__.copy()
