from typing import Dict, cast, TypeVar

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.database.database import Database
from control_server.src.database.database_collection import DatabaseCollection

T = TypeVar("T")


class MockDatabase(Database):
    """
    Instance of the database class representing a mock database
    """

    def __init__(self):
        super().__init__()
        self._collections: \
            Dict[DatabaseCollection, Dict[str, Deserializable]] = \
            {
                DatabaseCollection.USERS: {}
            }

    def set(
            self,
            collection: DatabaseCollection,
            entry_id: str,
            entry: IdentifyingClientData,
            overwrite: bool = False):
        collection = self._collections[collection]
        exists = entry_id in collection
        if overwrite or not exists:
            collection[entry_id] = entry
        elif not overwrite and exists:
            raise ValueError("Entry already exists")

    def delete(self, collection: DatabaseCollection, entry_id: str) -> bool:
        collection = self._collections[collection]
        if entry_id in collection:
            del collection[entry_id]
            return True

        return False

    def get_one(
            self,
            collection: DatabaseCollection,
            entry_id: str,
            entry_instance: T) -> T | None:
        collection = self._collections[collection]
        return collection[entry_id] if entry_id in collection else None

    def set_user(
            self,
            user_id: str,
            user: IdentifyingClientData,
            overwrite: bool = False):
        self.set(
            DatabaseCollection.USERS,
            user_id,
            user,
            overwrite
        )

    def delete_user(self, user_id: str) -> bool:
        return self.delete(DatabaseCollection.USERS, user_id)

    def get_user(self, user_id: str) -> IdentifyingClientData:
        return cast(
            IdentifyingClientData,
            self.get_one(
                DatabaseCollection.USERS,
                user_id,
                IdentifyingClientData()
            )
        )

    def clear(self):
        for collection in self._collections.values():
            collection.clear()
