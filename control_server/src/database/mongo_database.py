
from control_server.src.data.client_data import ClientData
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

    def set_user(self, user_id: str, user: ClientData):
        self._db[self._user_collection_name].insert_one(user.__dict__)

    def get_user(self, user_id: str) -> ClientData:
        raise NotImplementedError
