import uuid


class Task:
    """
    A class representing a client task
    """

    def __init__(
            self,
            name: str,
            data: str,
            min_delay: int,
            max_delay: int,
            client_id: str = None):
        self.name: str = name
        self.data: str = data
        self.min_delay: int = min_delay
        self.max_delay: int = max_delay
        self.client_id: str = client_id
        self.task_id: str = None

    def generate_id(self):
        self.task_id = str(uuid.uuid4())

    def serialize(self):
        return self.__dict__
