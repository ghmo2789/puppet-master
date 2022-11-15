class Task:
    """
    A class representing a client task
    """
    def __init__(self, name: str, data: str, min_delay: int, max_delay: int):
        self.name = name
        self.data = data
        self.min_delay = min_delay
        self.max_delay = max_delay

    def serialize(self):
        return self.__dict__
