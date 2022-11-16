import json

from control_server.src.data.client_data import ClientData
from control_server.src.data.identifying_client_data import \
    IdentifyingClientData
from control_server.src.database.database import Database
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

    def set_user(
            self,
            user_id: str,
            user: IdentifyingClientData,
            overwrite: bool = False):
        user_dict = user.serialize()

        user_id_dict = {
            "_id": user_id
        }

        complete_user_dict = {
            **user_dict,
            **user_id_dict
        }

        if overwrite:
            self._db[self._user_collection_name] \
                .update_one(
                    user_id_dict,
                    {
                        "$set": complete_user_dict
                    },
                    upsert=overwrite
                )
        else:
            self._db[self._user_collection_name].insert_one(user_dict)

    def delete_user(self, user_id: str) -> bool:
        result = self._db[self._user_collection_name].delete_one(
            {
                "_id": user_id
            })

        return result.deleted_count > 0

    def get_user(self, user_id: str) -> IdentifyingClientData | None:
        document = self._db[self._user_collection_name].find_one(
            {
                "_id": user_id
            })

        if document is None:
            return None

        return IdentifyingClientData(
            data_dict=dict(document)
        )

    def clear(self):
        self._db[self._user_collection_name].drop()
