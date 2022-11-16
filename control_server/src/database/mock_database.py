from control_server.src.data.client_data import ClientData
from control_server.src.database.database import Database


class MockDatabase(Database):
    """
    Instance of the database class representing a mock database
    """
    def __init__(self):
        super().__init__()
        self._users = {}

    def set_user(self, user_id: str, user: ClientData):
        self._users[user_id] = user

    def get_user(self, user_id: str) -> ClientData:
        raise NotImplementedError
