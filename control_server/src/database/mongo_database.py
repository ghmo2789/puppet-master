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

    def set(
            self,
            collection: DatabaseCollection,
            entry_id: str,
            entry: Serializable,
            overwrite: bool = False):
        entry_dict = entry.serialize()
        entry_id_dict = {
            "_id": entry_id
        }

        complete_entry_dict = entry_dict | entry_id_dict

        if overwrite:
            self._db[collection.get_name()] \
                .update_one(
                entry_id_dict,
                {
                    "$set": complete_entry_dict
                },
                upsert=overwrite
            )
        else:
            self._db[collection.get_name()].insert_one(complete_entry_dict)

    def delete(self, collection: DatabaseCollection, entry_id: str) -> bool:
        result = self._db[collection.get_name()].delete_one(
            {
                "_id": entry_id
            })

        return result.deleted_count > 0

    def get_one(
            self,
            collection: DatabaseCollection,
            entry_id: str,
            entry_instance: Deserializable) -> Deserializable | None:
        document = self._db[collection.get_name()].find_one(
            {
                "_id": entry_id
            })

        if document is None:
            return None

        entry_instance.deserialize(dict(document))
        return entry_instance

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
            DatabaseCollection.USERS,
            user_id
        )

    def get_user(self, user_id: str) -> IdentifyingClientData | None:
        return self.get_one(
            DatabaseCollection.USERS,
            user_id,
            IdentifyingClientData()
        )

    def clear(self):
        for collection_name in DatabaseCollection:
            self._db[collection_name].drop()
