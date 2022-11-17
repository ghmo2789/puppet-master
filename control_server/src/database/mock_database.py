from typing import Dict, cast

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.database.database import Database


class MockDatabase(Database):
    """
    Instance of the database class representing a mock database
    """

    def __init__(self):
        super().__init__()
        self._user_table = "users"
        self._collections: Dict[str, Dict[str, Deserializable]] = \
            {
                self._user_table: {}
            }

    def set(
            self,
            collection: str,
            entry_id: str,
            entry: IdentifyingClientData,
            overwrite: bool = False):
        collection = self._collections[collection]
        exists = entry_id in collection
        if overwrite or not exists:
            collection[entry_id] = entry
        elif not overwrite and exists:
            raise ValueError("Entry already exists")

    def delete(self, collection: str, entry_id: str) -> bool:
        collection = self._collections[collection]
        if entry_id in collection:
            del collection[entry_id]
            return True

        return False

    def get_one(
            self,
            collection: str,
            entry_id: str,
            entry_instance: Deserializable) -> Deserializable | None:
        collection = self._collections[collection]
        return collection[entry_id] if entry_id in collection else None

    def set_user(
            self,
            user_id: str,
            user: IdentifyingClientData,
            overwrite: bool = False):
        self.set(self._user_table, user_id, user, overwrite)

    def delete_user(self, user_id: str) -> bool:
        return self.delete(self._user_table, user_id)

    def get_user(self, user_id: str) -> IdentifyingClientData:
        return cast(
            IdentifyingClientData,
            self.get_one(self._user_table, user_id, IdentifyingClientData())
        )

    def clear(self):
        self._users = {}
