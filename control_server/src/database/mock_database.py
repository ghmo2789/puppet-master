from typing import Dict

from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.database.database import Database


class MockDatabase(Database):
    """
    Instance of the database class representing a mock database
    """
    def __init__(self):
        super().__init__()
        self._users: Dict[str, IdentifyingClientData] = {}

    def set_user(
            self,
            user_id: str,
            user: IdentifyingClientData,
            overwrite: bool = False):
        exists = user_id in self._users
        if overwrite or not exists:
            self._users[user_id] = user
        elif not overwrite and exists:
            raise ValueError("User already exists")

    def delete_user(self, user_id: str) -> bool:
        if user_id in self._users:
            del self._users[user_id]
            return True

        return False

    def get_user(self, user_id: str) -> IdentifyingClientData:
        return self._users[user_id] if user_id in self._users else None

    def clear(self):
        self._users = {}
