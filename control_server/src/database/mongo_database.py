from typing import List, Dict, Callable, Any

import pymongo

from control_server.src.data.deserializable import Deserializable
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.data.serializable import Serializable
from control_server.src.database.database import Database
from control_server.src.database.database_collection import DatabaseCollection
from control_server.src.database.database_credentials import DatabaseCredentials


class MongoDatabase(Database):
    """
    Instance of the database class representing a MongoDB database
    """

    def __init__(self):
        super().__init__()
        from pymongo import MongoClient

        self._credentials = DatabaseCredentials().read()
        self._client = MongoClient(
            self._credentials.mongo_host,
            port=int(self._credentials.mongo_port),
            username=self._credentials.mongo_user,
            password=self._credentials.mongo_password,
            # authSource=self.credentials.mongo_database,
            authMechanism=self._credentials.mongo_auth_mechanism
        )

        self._db = self._client[self._credentials.mongo_database]
        self._user_collection_name = "clients"

        self._db[DatabaseCollection.USER_TASKS].create_index(
            [
                ('client_id', pymongo.TEXT),
                ('task_id', pymongo.TEXT),
            ],
            name='search_index',
            default_language='english'
        )

    def set(
            self,
            collection: DatabaseCollection,
            entry: Serializable,
            entry_id: str = None,
            identifier: dict[str, Any] = None,
            overwrite: bool = False,
            ignore_id: bool = False):
        Database._verify_identifier_entry_id(entry_id, identifier)

        entry_dict = entry.serialize()
        entry_id_dict = {
            "_id": entry_id
        } if identifier is None else identifier

        complete_entry_dict = entry_dict | entry_id_dict

        if overwrite:
            if ignore_id:
                complete_entry_dict.pop("_id")

            self._db[collection.get_name()] \
                .update_one(
                entry_id_dict,
                {
                    "$set": complete_entry_dict
                },
                upsert=True
            )
        else:
            self._db[collection.get_name()].insert_one(complete_entry_dict)

    def delete(
            self,
            collection: DatabaseCollection,
            entry_id: str = None,
            identifier: dict[str, Any] = None) -> bool:
        Database._verify_identifier_entry_id(entry_id, identifier)
        id_dict = {
            "_id": entry_id
        } if identifier is None else identifier

        result = self._db[collection.get_name()].delete_one(id_dict)

        return result.deleted_count > 0

    def get_one(
            self,
            collection: DatabaseCollection,
            entry_id: str = None,
            identifier: dict[str, Any] = None,
            entry_instance: Deserializable = None) -> Deserializable | None:
        Database._verify_identifier_entry_id(entry_id, identifier)

        key = {
            "_id": entry_id
        } if entry_id is not None else identifier
        document = self._db[collection.get_name()].find_one(key)

        if document is None:
            return None

        entry_instance.deserialize(dict(document))
        return entry_instance

    def get_all(
            self,
            collection: DatabaseCollection,
            identifier: Dict[str, str],
            entry_instance_creator: Callable[[], Deserializable]
    ) -> List[Deserializable]:
        documents = self._db[collection.get_name()].find(identifier)

        for document in documents:
            if document is None:
                continue

            instance = entry_instance_creator()
            yield instance.deserialize(data_dict=dict(document))

    def set_user(
            self,
            user_id: str,
            user: IdentifyingClientData,
            overwrite: bool = False):
        self.set(
            collection=DatabaseCollection.USERS,
            entry_id=user_id,
            entry=user,
            overwrite=overwrite
        )

    def delete_user(self, user_id: str) -> bool:
        return self.delete(
            collection=DatabaseCollection.USERS,
            entry_id=user_id
        )

    def get_user(self, user_id: str) -> IdentifyingClientData | None:
        return self.get_one(
            collection=DatabaseCollection.USERS,
            entry_id=user_id,
            entry_instance=IdentifyingClientData()
        )

    def clear(self):
        for collection_name in DatabaseCollection:
            self._db[collection_name].drop()
