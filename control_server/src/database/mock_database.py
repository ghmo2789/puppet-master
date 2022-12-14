from collections import OrderedDict
from typing import Dict, cast, TypeVar, List, Any, Callable

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.database.database import Database
from control_server.src.database.database_collection import DatabaseCollection
from control_server.tests.utils.hashable_dict import HashableDict

T = TypeVar("T")


class MockDatabase(Database):
    """
    Instance of the database class representing a mock database
    """

    def __init__(self):
        super().__init__()
        self._collections: \
            Dict[
                DatabaseCollection,
                OrderedDict[str | HashableDict, Deserializable]
            ] = \
            {
                DatabaseCollection.CLIENTS: OrderedDict(),
                DatabaseCollection.CLIENT_TASKS: OrderedDict(),
                DatabaseCollection.CLIENT_TASK_RESPONSES: OrderedDict(),
                DatabaseCollection.CLIENT_DONE_TASKS: OrderedDict()
            }

    def set(
            self,
            collection: DatabaseCollection,
            entry: IdentifyingClientData,
            entry_id: str = None,
            identifier: dict[str, Any] = None,
            overwrite: bool = False,
            ignore_id: bool = False):
        Database._verify_identifier_entry_id(entry_id, identifier)

        if collection not in self._collections:
            self._collections[collection] = OrderedDict()

        collection = self._collections[collection]
        key = identifier if identifier is not None else entry_id
        key = HashableDict(key) if isinstance(key, dict) else key

        exists = key in collection

        if overwrite or not exists:
            collection[key] = entry
        elif not overwrite and exists:
            raise ValueError("Entry already exists")

    def delete(
            self,
            collection: DatabaseCollection,
            entry_id: str = None,
            identifier: dict[str, Any] = None) -> bool:
        collection = self._collections[collection]
        key = identifier if identifier is not None else entry_id
        key = HashableDict(key) if isinstance(key, dict) else key

        if key in collection:
            del collection[key]
            return True

        return False

    def get_one(
            self,
            collection: DatabaseCollection,
            entry_id: str = None,
            identifier: dict[str, Any] = None,
            entry_instance: Deserializable = None) -> Deserializable | None:
        Database._verify_identifier_entry_id(entry_id, identifier)
        collection = self._collections[collection]

        if entry_id is not None:
            if isinstance(entry_id, dict):
                entry_id = HashableDict(entry_id)

            return collection[entry_id] if entry_id in collection else None
        else:
            return next(
                (entry for entry in collection.values() if
                 all(
                     identifier[key] == MockDatabase._get_attribute(entry, key)
                     for key in identifier
                 )),
                None
            )

    @staticmethod
    def _get_attribute(value: Any, attribute: str):
        sub_attributes = attribute.split(".")
        current_value = value
        for sub_attribute in sub_attributes:
            if isinstance(current_value, dict):
                current_value = current_value[sub_attribute]
            else:
                current_value = getattr(current_value, sub_attribute)

        return current_value

    def get_all(
            self,
            collection: DatabaseCollection,
            identifier: Dict[str, str],
            entry_instance_creator: Callable[[], Deserializable]
    ) -> List[Deserializable]:
        collection = self._collections[collection]
        for entry in collection.values():
            if all(
                    identifier[key] == MockDatabase._get_attribute(entry, key)
                    for key in identifier
            ):
                yield entry

    def set_client(
            self,
            client_id: str,
            client: IdentifyingClientData,
            overwrite: bool = False):
        self.set(
            DatabaseCollection.CLIENTS,
            entry_id=client_id,
            entry=client,
            overwrite=overwrite
        )

    def delete_client(self, client_id: str) -> bool:
        return self.delete(
            collection=DatabaseCollection.CLIENTS,
            entry_id=client_id
        )

    def get_client(self, client_id: str) -> IdentifyingClientData:
        return cast(
            IdentifyingClientData,
            self.get_one(
                collection=DatabaseCollection.CLIENTS,
                entry_id=client_id,
                entry_instance=IdentifyingClientData()
            )
        )

    def clear(self):
        for collection in self._collections.values():
            collection.clear()
