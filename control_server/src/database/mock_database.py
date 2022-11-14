from control_server.src.data.client_data import ClientData
from control_server.src.database.db import Database


class MockDatabase(Database):
    def __init__(self):
        super().__init__()
        self._users = {}

    def set_user(self, user_id: str, user: ClientData):
        self._users[user_id] = user
